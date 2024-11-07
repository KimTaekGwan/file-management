import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from monitor.websocket import manager
import asyncio

target_folder_path = r"C:\Users\WEVEN_PC\Desktop\project\file-management\monitored"
log_directory = "logs"
log_file_path = os.path.join(log_directory, 'watchdog.log')


# 로깅 설정
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, encoding='utf-8'),
        logging.StreamHandler()  # 콘솔 출력도 유지
    ]
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
    def __init__(self, target_folder_path):
        super().__init__()
        self.target_folder_path = target_folder_path
        self.last_modified = {}
        self.cooldown = 1
        self.recently_created = set()  # 최근 생성된 파일 추적

    def get_file_metadata(self, file_path):
        try:
            stat = os.stat(file_path)
            name, ext = os.path.splitext(file_path)
            basename = os.path.basename(file_path)
            
            # 숨김 파일 여부 확인
            is_hidden = basename.startswith('.')
            
            return {
                "size": stat.st_size,
                "created": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime)),
                "modified": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime)),
                "name": basename,
                "extension": ext[1:] if ext else "없음",
                "is_hidden": is_hidden,
                "path": file_path
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {e}")
            return None

    def notify_clients(self, event_type: str, file_path: str):
        if event_type == "deleted":
            # 삭제 이벤트의 경우 기본 정보만 전송
            message = {
                "type": event_type,
                "metadata": {
                    "path": file_path,
                    "name": os.path.basename(file_path)
                },
                "timestamp": time.time()
            }
            manager.sync_notify(message)
        else:
            # 다른 이벤트의 경우 기존 로직 유지
            metadata = self.get_file_metadata(file_path)
            if metadata:
                message = {
                    "type": event_type,
                    "metadata": metadata,
                    "timestamp": time.time()
                }
                manager.sync_notify(message)
            

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")
            self.recently_created.add(event.src_path)
            self.notify_clients("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            # 최근 생성된 파일의 수정 이벤트는 무시
            if event.src_path in self.recently_created:
                self.recently_created.remove(event.src_path)
                return
                
            current_time = time.time()
            last_modified = self.last_modified.get(event.src_path, 0)
            if current_time - last_modified > self.cooldown:
                logger.info(f"File modified: {event.src_path}")
                self.last_modified[event.src_path] = current_time
                self.notify_clients("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            # recently_created 세트에서 제거
            if event.src_path in self.recently_created:
                self.recently_created.remove(event.src_path)
            # last_modified 딕셔너리에서 제거
            if event.src_path in self.last_modified:
                del self.last_modified[event.src_path]
            self.notify_clients("deleted", event.src_path)

class WatchdogThread:
    def __init__(self, target_folder_path):
        self.observer = Observer()
        self.target_folder_path = target_folder_path
        self.is_running = False

    def start(self):
        try:
            if not exists_folder(self.target_folder_path):
                logger.error(f"Failed to start monitoring: {self.target_folder_path}")
                return
            
            event_handler = FolderHandler(self.target_folder_path)
            self.observer.schedule(event_handler, self.target_folder_path, recursive=True)
            self.observer.start()
            self.is_running = True
            logger.info(f"Started monitoring: {self.target_folder_path}")
        except Exception as e:
            logger.error(f"Error starting watchdog: {e}")

    def stop(self):
        try:
            if self.observer and self.is_running:
                self.observer.stop()
                self.observer.join()
                self.is_running = False
                logger.info("Monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping watchdog: {e}")
