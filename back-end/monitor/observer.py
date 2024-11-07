import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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
        self.cooldown = 1  # 1초의 쿨다운 시간

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")
            # 여기에 파일 생성 시 추가 처리 로직 구현 가능

    def on_modified(self, event):
        if not event.is_directory:
            current_time = time.time()
            last_modified = self.last_modified.get(event.src_path, 0)
            
            # 마지막 수정 시간과 현재 시간을 비교하여 쿨다운 시간 이내인 경우 무시
            if current_time - last_modified > self.cooldown:
                logger.info(f"File modified: {event.src_path}")
                self.last_modified[event.src_path] = current_time
                # 여기에 파일 수정 시 추가 처리 로직 구현 가능

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")
            # 여기에 파일 삭제 시 추가 처리 로직 구현 가능

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
