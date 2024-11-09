import os
import time
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from websocket.file_monitor_ws import file_monitor_manager

target_folder_path = "volumes/monitored"
log_directory = "logs"
log_file_path = os.path.join(log_directory, "watchdog.log")


# 로깅 설정
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path, encoding="utf-8"),
        logging.StreamHandler(),  # 콘솔 출력도 유지
    ],
)
logger = logging.getLogger(__name__)


def exists_folder(folder_path):
    if not os.path.exists(folder_path):
        try:
            os.makedirs(folder_path)
            logger.info(f"Created directory: {folder_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory: {e}")
            return False
    return True


class FolderHandler(FileSystemEventHandler):
    def __init__(self, target_folder_path, file_system):
        super().__init__()
        self.target_folder_path = target_folder_path
        self.file_system = file_system
        self.last_modified = {}
        self.cooldown = 1
        self.recently_created = set()  # 최근 생성된 파일 추적
        self.creation_cooldown = 2  # 생성 이벤트 후 수정 이벤트 무시 시간

    def get_file_metadata(self, file_path):
        try:
            stat = os.stat(file_path)
            name, ext = os.path.splitext(file_path)
            basename = os.path.basename(file_path)

            return {
                "size": stat.st_size,
                "created": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime)
                ),
                "modified": time.strftime(
                    "%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)
                ),
                "name": basename,
                "extension": ext[1:] if ext else "없음",
                "is_hidden": basename.startswith("."),
                "path": file_path,
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            return None

    def notify_clients(self, event_type: str, file_path: str):
        if event_type == "deleted":
            # 삭제 이벤트의 경우 기본 정보만 전송
            message = {
                "type": event_type,
                "metadata": {"path": file_path, "name": os.path.basename(file_path)},
                "timestamp": time.time(),
            }
            file_monitor_manager.sync_notify(message)
        else:
            # 다른 이벤트의 경우 기존 로직 유지
            metadata = self.get_file_metadata(file_path)
            if metadata:
                message = {
                    "type": event_type,
                    "metadata": metadata,
                    "timestamp": time.time(),
                }
                file_monitor_manager.sync_notify(message)

    def on_created(self, event):
        abs_path = os.path.abspath(event.src_path)
        logger.info(
            f"{'Directory' if event.is_directory else 'File'} created: {abs_path}"
        )

        # 이미 존재하는 경로인지 확인
        existing_node = self.file_system.get_node_by_path(abs_path)
        if existing_node:
            logger.info(f"Node already exists for path: {abs_path}")
            return

        # 파일 시스템에 노드 추가
        metadata = self.get_file_metadata(abs_path)
        if metadata:
            node = self.file_system.create_node(
                abs_path, is_directory=event.is_directory
            )
            node.metadata = metadata
            self.recently_created.add(abs_path)
            self.last_modified[abs_path] = time.time()
            # 클라이언트에 생성 이벤트 알림
            self.notify_clients("created", abs_path)
        else:
            logger.error(f"Failed to get metadata for: {abs_path}")

    def on_modified(self, event):
        if not event.is_directory:
            current_time = time.time()
            abs_path = os.path.abspath(event.src_path)

            # 최근 생성된 파일의 수정 이벤트인 경우 무시
            if abs_path in self.recently_created:
                last_created_time = self.last_modified.get(abs_path, 0)
                if current_time - last_created_time < self.creation_cooldown:
                    return
                self.recently_created.remove(abs_path)

            last_modified = self.last_modified.get(abs_path, 0)
            if current_time - last_modified > self.cooldown:
                logger.info(f"File modified: {abs_path}")

                if not os.path.exists(abs_path):
                    logger.warning(f"Modified file does not exist: {abs_path}")
                    return

                metadata = self.get_file_metadata(abs_path)
                if metadata:
                    self.file_system.update_node(abs_path, metadata)
                    self.last_modified[abs_path] = current_time
                    self.notify_clients("modified", abs_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")

            # recently_created 세트에서 제거
            if event.src_path in self.recently_created:
                self.recently_created.remove(event.src_path)
            # last_modified 딕셔너리에서 제거
            if event.src_path in self.last_modified:
                del self.last_modified[event.src_path]

            # 파일 시스템에서 노드 제거
            self.file_system.remove_node(event.src_path)
            self.notify_clients("deleted", event.src_path)

    def copy_file(self, src_path: str, dest_path: str):
        try:
            if os.path.exists(src_path):
                shutil.copy2(src_path, dest_path)
                logger.info(f"File copied from {src_path} to {dest_path}")
                return True
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            return False


class WatchdogThread:
    def __init__(self, target_folder_path, file_system):
        self.observer = Observer()
        self.target_folder_path = target_folder_path
        self.file_system = file_system
        self.is_running = False

    def start(self):
        try:
            if not exists_folder(self.target_folder_path):
                logger.error(f"Failed to start monitoring: {self.target_folder_path}")
                return

            event_handler = FolderHandler(self.target_folder_path, self.file_system)
            self.observer.schedule(
                event_handler, self.target_folder_path, recursive=True
            )
            self.observer.start()
            self.is_running = True
        except Exception as e:
            logger.error(f"Error starting observer: {e}")

    def stop(self):
        try:
            if self.observer and self.is_running:
                self.observer.stop()
                self.observer.join()
                self.is_running = False
                logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping watchdog: {e}")
