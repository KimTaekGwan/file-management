from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from monitor.observer import WatchdogThread, target_folder_path

app = FastAPI()

watchdog_thread = WatchdogThread(target_folder_path)


@app.on_event("startup")
async def startup_event():
    watchdog_thread.start()


@app.on_event("shutdown")
async def shutdown_event():
    watchdog_thread.stop()
