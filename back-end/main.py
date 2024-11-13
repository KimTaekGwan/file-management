import os
import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from routes import monitor, api
from monitor.observer import WatchdogThread, target_folder_path

# from monitor.websocket import manager
from indexer.filesystem import FileSystem
from indexer.scanner import FileSystemScanner
from websocket.file_monitor_ws import file_monitor_manager
from websocket.file_system_ws import FileSystemManager
from indexer.file_indexer import FileIndexer

# 로그 디렉토리 설정
LOG_DIRECTORY = os.path.join(os.path.dirname(__file__), "logs")

# FileIndexer 초기화
file_indexer = FileIndexer(LOG_DIRECTORY)

# FileSystem 초기화 (FileIndexer 주입)
file_system = FileSystem(file_indexer)

# WatchdogThread 및 FileSystemManager 초기화
watchdog_thread = WatchdogThread(target_folder_path, file_system)
file_system_manager = FileSystemManager(file_system)  # 추가


async def start():
    print("Service is starting...")
    
    # 로그 디렉토리 생성
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    print(f"Log directory initialized: {LOG_DIRECTORY}")
    
    # 파일 시스템 초기화
    scanner = FileSystemScanner(target_folder_path, file_system)
    print(f"Scanning directory: {target_folder_path}")
    scanner.scan()
    print("Scan completed")

    if not file_system.root:
        print("Warning: File system root is not initialized!")
        print(f"Available nodes: {list(file_system.nodes.keys())}")
    else:
        print(f"Root node initialized: {file_system.root.uuid}")
        
    # FileIndexer 상태 확인
    print(f"FileIndexer initialized with {len(file_indexer.index)} indexed files")
    print(f"File history contains {len(file_indexer.history)} events")

    # Start watchdog thread and process queues
    watchdog_thread.start()
    asyncio.create_task(file_monitor_manager.process_queue())
    asyncio.create_task(file_system_manager.process_queue())

async def shutdown():
    print("Service is shutting down...")
    watchdog_thread.stop()
    file_monitor_manager.stop()
    file_system_manager.stop()
    # manager.stop()
    file_indexer.save_index()
    file_indexer.save_history()
    print("FileIndexer data saved")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start()
    yield
    await shutdown()


def include_router(app: FastAPI):
    api.initialize_router(file_system)
    monitor.initialize_router(file_system_manager)  # 이미 생성된 manager 전달
    app.include_router(monitor.router, prefix="/ws", tags=["websocket"])
    app.include_router(api.router, prefix="/api", tags=["api"])


def start_application():
    app = FastAPI(
        title="FastAPI",
        summary="Deadpool's favorite app. Nuff said.",
        # docs_url=None,
        # redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=JSONResponse,
        lifespan=lifespan,
        swagger_ui_parameters={
            "syntaxHighlight.theme": "obsidian"
        },  # 테마 설정 - 글씨 색상 변경
    )

    # origins = ["*"]
    origins = [
        "http://localhost",
        "http://localhost:5173",  # Vite 기본 포트
        "http://127.0.0.1:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        # allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_router(app)
    return app


app = start_application()
