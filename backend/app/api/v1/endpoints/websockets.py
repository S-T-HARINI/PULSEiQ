import json
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket client connections for real-time grid telemetry broadcasting."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, message: dict) -> None:
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()


@router.websocket("/ws/grid")
async def grid_telemetry_stream(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint for grid state telemetry and event broadcasting.
    Ready for future live power-flow and simulation event streaming.
    """
    await manager.connect(websocket)
    try:
        # Send initial connection confirmation frame
        await websocket.send_json({
            "event": "connection_established",
            "status": "connected",
            "channel": "grid_telemetry",
            "message": "PULSEiQ real-time Grid WebSocket stream ready.",
        })
        while True:
            text_data = await websocket.receive_text()
            try:
                payload = json.loads(text_data)
            except Exception:
                payload = {"raw": text_data}

            # Echo acknowledgment frame for client heartbeats and control messages
            await websocket.send_json({
                "event": "acknowledgment",
                "status": "received",
                "payload": payload,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Alias route maintained for backward compatibility
@router.websocket("/ws/live")
async def live_stream_alias(websocket: WebSocket) -> None:
    """Live stream route alias forwarding to grid telemetry stream."""
    await grid_telemetry_stream(websocket)
