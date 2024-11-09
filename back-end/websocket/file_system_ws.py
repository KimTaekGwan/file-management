from fastapi import WebSocket
from indexer.filesystem import FileSystem
from .websocket_base import WebSocketManagerBase


class FileSystemManager(WebSocketManagerBase):
    def __init__(self, file_system: FileSystem):
        super().__init__()
        self.file_system = file_system
        self.file_system.subscribe(self.handle_filesystem_event)

    def handle_filesystem_event(self, event_type: str, node):
        # 파일 시스템 이벤트를 웹소켓으로 전달
        message = {
            "type": event_type,
            "node": {
                "uuid": node.uuid,
                "name": node.name,
                "path": node.path,
                "is_directory": node.is_directory,
                "metadata": node.metadata,
            },
        }
        self.sync_notify(message)

    async def handle_client_message(self, websocket: WebSocket, message: dict):
        # 파일 시스템 관련 클라이언트 메시지 처리
        if message.get("action") == "get_tree":
            await self.send_filesystem_tree(websocket)

    async def send_filesystem_tree(self, websocket: WebSocket):
        # 파일 시스템 트리 정보 전송
        if self.file_system.root:
            tree = self.build_tree(self.file_system.root)
            await websocket.send_json({"type": "filesystem_tree", "data": tree})

    def build_tree(self, node):
        return {
            "uuid": node.uuid,
            "name": node.name,
            "path": node.path,
            "is_directory": node.is_directory,
            "metadata": node.metadata,
            "children": [self.build_tree(child) for child in node.children],
        }
