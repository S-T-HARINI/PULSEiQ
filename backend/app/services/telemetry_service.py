import asyncio
import logging
import math
import time
from datetime import datetime, timezone
from typing import Optional

from backend.app.schemas.telemetry import (
    GridOperationalStatus,
    GridTelemetryMessage,
)
from backend.app.services.grid_service import grid_service
from backend.app.services.connection_manager import ws_connection_manager
from backend.app.core.config import settings

logger = logging.getLogger("pulseiq.telemetry_service")


class TelemetryService:
    """Async service responsible for generating realistic real-time telemetry frames
    and streaming updates to connected WebSocket clients.
    """

    def __init__(self) -> None:
        self._tick: int = 0
        self._background_task: Optional[asyncio.Task] = None
        self._running: bool = False
        self._override_risk: Optional[float] = None
        self._override_status: Optional[GridOperationalStatus] = None
        self._override_affected_components: list = []

    def generate_current_telemetry(self) -> GridTelemetryMessage:
        """Generates a structured, physics-bounded real-time grid telemetry snapshot."""
        self._tick += 1
        now_ts = time.time()
        grid_state = grid_service.get_grid_state()
        summary = grid_state.summary

        # Realistic subtle time-series fluctuations (±1.5% oscillation)
        variation_factor = 1.0 + (0.015 * math.sin(now_ts * 0.35 + self._tick * 0.1))
        wind_gust = 0.02 * math.cos(now_ts * 0.25 + self._tick * 0.15)

        base_gen = summary.total_generation_mw
        base_dem = summary.total_demand_mw

        total_gen = round(base_gen * (1.0 + (0.012 * math.sin(now_ts * 0.2 + self._tick * 0.1))), 2)
        total_dem = round(base_dem * variation_factor, 2)

        # Solar and wind telemetry
        solar_node = grid_service.get_node_by_id("gen-solar-1")
        wind_node = grid_service.get_node_by_id("gen-wind-1")
        solar_mw = (solar_node.current_output_mw if solar_node else 140.0) * (1.0 + 0.01 * math.sin(now_ts * 0.15))
        wind_mw = (wind_node.current_output_mw if wind_node else 95.0) * (1.0 + wind_gust)
        renewable_total = solar_mw + wind_mw

        renewable_pct = round((renewable_total / total_gen) * 100, 2) if total_gen > 0 else 0.0

        # Frequency response to momentary generation-demand delta + governor damping
        delta_p = total_gen - total_dem
        freq_swing = (0.025 * math.sin(now_ts * 0.75 + self._tick * 0.4)) + (0.012 * math.cos(now_ts * 1.35))
        raw_freq = 50.00 + (delta_p * 0.0006) + freq_swing
        # Bound strictly within standard grid tolerance [49.95, 50.05]
        frequency = round(max(49.95, min(50.05, raw_freq)), 3)

        # Battery state of charge (subtle discharge trend)
        battery_soc = max(10.0, min(100.0, round(summary.battery_soc - (0.01 * (self._tick % 50)), 2)))

        # Risk calculation and classification
        risk_index = self._override_risk if self._override_risk is not None else summary.grid_risk_index

        if self._override_status:
            status = self._override_status
        elif risk_index >= 0.70:
            status = GridOperationalStatus.CRITICAL
        elif risk_index >= 0.45:
            status = GridOperationalStatus.WARNING
        else:
            status = GridOperationalStatus.NORMAL

        affected = list(self._override_affected_components)
        if status != GridOperationalStatus.NORMAL and not affected:
            affected = ["line-north-central-1"]

        return GridTelemetryMessage(
            message_type="grid_telemetry",
            timestamp=datetime.now(timezone.utc).isoformat(),
            grid_status=status,
            total_generation=total_gen,
            total_demand=total_dem,
            renewable_generation_percent=min(100.0, max(0.0, renewable_pct)),
            battery_soc=battery_soc,
            grid_risk_index=min(1.0, max(0.0, round(risk_index, 3))),
            frequency_hz=frequency,
            line_utilization_avg=56.4,
            affected_components=affected,
            details={
                "solar_generation_mw": round(solar_mw, 2),
                "wind_generation_mw": round(wind_mw, 2),
                "net_imbalance_mw": round(delta_p, 2),
                "active_connections": ws_connection_manager.get_active_count(),
            },
        )

    def set_scenario_impact(self, risk_index: float, status: GridOperationalStatus, affected_components: list) -> None:
        """Allows what-if scenarios or simulations to reflect their state in real-time telemetry."""
        self._override_risk = risk_index
        self._override_status = status
        self._override_affected_components = affected_components

    def reset_scenario_impact(self) -> None:
        """Resets telemetry overrides back to nominal baseline."""
        self._override_risk = None
        self._override_status = None
        self._override_affected_components = []

    async def broadcast_telemetry_loop(self) -> None:
        """Periodic async loop continuously publishing telemetry frames to connected clients."""
        interval = max(0.5, settings.TELEMETRY_INTERVAL_SECONDS)
        logger.info(f"Starting real-time grid telemetry broadcasting loop (interval: {interval}s).")
        self._running = True

        while self._running:
            try:
                if ws_connection_manager.get_active_count() > 0:
                    snapshot = self.generate_current_telemetry()
                    await ws_connection_manager.broadcast(snapshot)
            except Exception as e:
                logger.warning(f"Error in telemetry broadcast loop: {e}")

            await asyncio.sleep(interval)

    def start_background_broadcaster(self) -> None:
        """Launches the background broadcast loop as an asyncio Task."""
        if not self._running:
            try:
                loop = asyncio.get_running_loop()
                self._background_task = loop.create_task(self.broadcast_telemetry_loop())
            except RuntimeError:
                pass

    def stop_background_broadcaster(self) -> None:
        """Stops the background broadcast task."""
        self._running = False
        if self._background_task and not self._background_task.done():
            self._background_task.cancel()


telemetry_service = TelemetryService()
