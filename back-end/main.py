from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
import os
from fastapi.middleware.cors import CORSMiddleware
from routes import monitor, api
from monitor.observer import WatchdogThread, target_folder_path
from monitor.websocket import manager
import asyncio
app = FastAPI()

# 라우터 등록
app.include_router(monitor.router, prefix="/monitor", tags=["monitor"])
app.include_router(api.router, prefix="/api", tags=["api"])

# CORS 설정 추가 (개발 환경용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # SvelteKit 기본 개발 서버 포트
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 프로덕션 환경에서만 정적 파일 제공
if os.getenv("ENV") == "production":
    app.mount("/", StaticFiles(directory="front-end/build"), name="front-end")

watchdog_thread = WatchdogThread(target_folder_path)

@app.on_event("startup")
async def startup_event():
    watchdog_thread.start()
    try:
        asyncio.create_task(manager.process_queue())
    except Exception as e:
        print(f"Error creating process_queue task: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    watchdog_thread.stop()
    manager.stop()
