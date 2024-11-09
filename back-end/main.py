import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from routes import monitor, api
from monitor.observer import WatchdogThread, target_folder_path
from monitor.websocket import manager
from indexer.filesystem import FileSystem
from indexer.scanner import FileSystemScanner

file_system = FileSystem()
watchdog_thread = WatchdogThread(target_folder_path, file_system)


async def start():
    print("service is started.")
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

    # Start watchdog thread and process queue
    watchdog_thread.start()
    asyncio.create_task(manager.process_queue())


def shutdown():
    print("service is stopped.")
    # Stop watchdog thread and manager
    watchdog_thread.stop()
    manager.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start()
    yield
    shutdown()


def include_router(app: FastAPI):
    api.initialize_router(file_system)
    app.include_router(monitor.router, prefix="/monitor", tags=["monitor"])
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
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    include_router(app)
    return app


app = start_application()
