from abc import ABC, abstractmethod
from fastapi import WebSocket
from typing import List
import asyncio
from queue import Queue
import logging

logger = logging.getLogger(__name__)


class WebSocketManagerBase(ABC):
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.message_queue = Queue()
        self.is_running = True

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)

        for conn in disconnected:
            try:
                self.active_connections.remove(conn)
            except ValueError:
                pass

    def sync_notify(self, message: dict):
        self.message_queue.put(message)

    async def process_queue(self):
        while self.is_running:
            try:
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    await self.broadcast(message)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in process_queue: {e}")
                continue

    def stop(self):
        self.is_running = False

    @abstractmethod
    async def handle_client_message(self, websocket: WebSocket, message: dict):
        pass
