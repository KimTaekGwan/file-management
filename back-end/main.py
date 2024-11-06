from fastapi import FastAPI, Depends
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy.orm import Session

app = FastAPI()


class FolderHandler(FileSystemEventHandler):
    def __init__(self, target_folder_path, db: Session):
        super().__init__()
        self.target_folder_path = target_folder_path
        self.db = db

    def on_created(self, event):
        if not event.is_directory:
            print(f"파일 생성: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            print(f"파일 수정: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"파일 삭제: {event.src_path}")


class WatchdogThread:
    def __init__(self, target_folder_path):
        self.observer = Observer()
        self.target_folder_path = target_folder_path

    def start(self):
        event_handler = FolderHandler(self.target_folder_path)
        self.observer.schedule(event_handler, self.target_folder_path, recursive=True)
        self.observer.start()
        print(f"모니터링 시작: {self.target_folder_path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        print("모니터링 종료")


target_folder_path = "/monitored"
watchdog_thread = WatchdogThread(target_folder_path)


@app.on_event("startup")
async def startup_event():
    watchdog_thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    watchdog_thread.stop()
