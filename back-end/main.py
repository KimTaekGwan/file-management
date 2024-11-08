import asyncio
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from routes import monitor, api
from monitor.observer import WatchdogThread, target_folder_path
from monitor.websocket import manager

watchdog_thread = WatchdogThread(target_folder_path)


async def start():
    print("service is started.")
    # Start watchdog thread and process queue
    watchdog_thread.start()
    try:
        asyncio.create_task(manager.process_queue())
    except Exception as e:
        print(f"Error creating process_queue task: {e}")


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

    origins =["http://localhost:5173"],  # SvelteKit 기본 개발 서버 포트
    # origins = ["*"]
    # origins = [
    #     "http://localhost.tiangolo.com",
    #     "https://localhost.tiangolo.com",
    #     "http://localhost",
    #     "http://localhost:8080",
    # ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_router(app)
    return app

app = start_application()

