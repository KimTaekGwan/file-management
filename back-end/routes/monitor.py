from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.file_monitor_ws import file_monitor_manager
from websocket.file_system_ws import FileSystemManager
import json

router = APIRouter()
filesystem_manager = None


def initialize_router(manager: FileSystemManager):
    global filesystem_manager
    filesystem_manager = manager


@router.websocket("/monitor")
async def file_monitor_endpoint(websocket: WebSocket):
    await file_monitor_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await file_monitor_manager.handle_client_message(
                websocket, json.loads(data)
            )
    except WebSocketDisconnect:
        file_monitor_manager.disconnect(websocket)


@router.websocket("/filesystem")
async def filesystem_endpoint(websocket: WebSocket):
    await filesystem_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await filesystem_manager.handle_client_message(websocket, json.loads(data))
    except WebSocketDisconnect:
        filesystem_manager.disconnect(websocket)
