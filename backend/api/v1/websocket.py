"""WebSocket API for real-time communication"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
import json
import asyncio

from backend.core.security import decode_token

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        # session_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a session"""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()

        self.active_connections[session_id].add(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket from a session"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)

            # Remove session if no connections left
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    async def send_message(self, message: dict, session_id: str, exclude: WebSocket = None):
        """Send message to all connections in a session"""
        if session_id not in self.active_connections:
            return

        # Send to all connections except the sender
        for connection in self.active_connections[session_id]:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection closed, will be cleaned up on next disconnect
                    pass

    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        for connections in self.active_connections.values():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
):
    """WebSocket endpoint for real-time updates"""

    # Verify JWT token
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=1008, reason="Invalid token")
        return

    # Connect
    await manager.connect(websocket, session_id)

    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "session_id": session_id,
        })

        # Ping/pong heartbeat
        heartbeat_task = asyncio.create_task(heartbeat(websocket))

        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

            elif message.get("type") == "chat":
                # Broadcast chat message to session
                await manager.send_message(
                    {
                        "type": "chat",
                        "content": message.get("content"),
                        "user_id": user_id,
                        "timestamp": message.get("timestamp"),
                    },
                    session_id,
                    exclude=websocket,
                )

            elif message.get("type") == "cursor":
                # Broadcast cursor position
                await manager.send_message(
                    {
                        "type": "cursor",
                        "user_id": user_id,
                        "position": message.get("position"),
                    },
                    session_id,
                    exclude=websocket,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

        # Notify others of disconnection
        await manager.send_message(
            {
                "type": "user_disconnect",
                "user_id": user_id,
            },
            session_id,
        )

    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)

    finally:
        heartbeat_task.cancel()


async def heartbeat(websocket: WebSocket):
    """Send periodic heartbeat to keep connection alive"""
    try:
        while True:
            await asyncio.sleep(30)  # 30 seconds
            await websocket.send_json({"type": "heartbeat"})
    except Exception:
        pass
