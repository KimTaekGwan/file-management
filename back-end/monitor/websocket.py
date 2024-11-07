from fastapi import WebSocket
from typing import List
import asyncio
from queue import Queue
import json

class ConnectionManager:
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
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.active_connections.remove(conn)

    def sync_notify(self, message: dict):
        self.message_queue.put(message)

    async def process_queue(self):
        try:
            while self.is_running:
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    await self.broadcast(message)
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Error in process_queue: {e}")

    def stop(self):
        self.is_running = False

manager = ConnectionManager()