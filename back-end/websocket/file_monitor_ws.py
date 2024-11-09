from fastapi import WebSocket
from .websocket_base import WebSocketManagerBase


class FileMonitorManager(WebSocketManagerBase):
    async def handle_client_message(self, websocket: WebSocket, message: dict):
        # 파일 모니터링 관련 클라이언트 메시지 처리
        pass


file_monitor_manager = FileMonitorManager()
