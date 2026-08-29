import logging
from typing import List, Set
from fastapi import WebSocket
from backend.app.schemas.telemetry import GridTelemetryMessage

logger = logging.getLogger("pulseiq.websocket")


class ConnectionManager:
    """Manages active client WebSocket connections for real-time grid telemetry broadcasting."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accepts an incoming WebSocket connection and registers the client."""
        await websocket.accept()
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        """Removes a disconnected client from the active registry."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Remaining active: {len(self.active_connections)}")

    async def send_message(self, websocket: WebSocket, message: GridTelemetryMessage) -> None:
        """Sends a typed telemetry message to a specific client."""
        try:
            await websocket.send_json(message.model_dump())
        except Exception as e:
            logger.debug(f"Failed sending to client: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: GridTelemetryMessage) -> None:
        """Broadcasts a typed telemetry snapshot to all currently connected clients."""
        if not self.active_connections:
            return

        dead_connections: List[WebSocket] = []
        payload = message.model_dump()

        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:
                logger.debug(f"Error broadcasting to client, queuing removal: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    def get_active_count(self) -> int:
        """Returns the number of currently active client connections."""
        return len(self.active_connections)


ws_connection_manager = ConnectionManager()
