from fastapi import APIRouter, WebSocket
from monitor.websocket import manager

router = APIRouter()


@router.get("/status")
async def get_status():
    return {"status": "running"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(websocket)