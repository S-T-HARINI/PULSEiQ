import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("pulseiq.ai_bridge")


class AIModuleBridge:
    """Integration bridge between the FastAPI backend and Person 3's AI/ML modules.
    Provides graceful detection, execution, and deterministic fallback handling
    so the backend remains fully operational whether the AI modules are present,
    being trained, or running in external workers.
    """

    def __init__(self) -> None:
        self._forecast_module: Optional[Any] = None
        self._simulation_module: Optional[Any] = None
        self._risk_module: Optional[Any] = None
        self._optimization_module: Optional[Any] = None
        self._discover_modules()

    def _discover_modules(self) -> None:
        """Attempts to dynamically import Person 3's AI/ML packages."""
        # 1. Forecasting module
        try:
            import ai.forecasting as fc_mod  # type: ignore
            self._forecast_module = fc_mod
            logger.info("Successfully bound Person 3 AI Forecasting module.")
        except (ImportError, ModuleNotFoundError):
            try:
                import ai.forecast as fc_mod  # type: ignore
                self._forecast_module = fc_mod
                logger.info("Successfully bound Person 3 AI Forecast module.")
            except (ImportError, ModuleNotFoundError):
                self._forecast_module = None

        # 2. Simulation engine
        try:
            import ai.simulation as sim_mod  # type: ignore
            self._simulation_module = sim_mod
            logger.info("Successfully bound Person 3 AI Simulation engine.")
        except (ImportError, ModuleNotFoundError):
            self._simulation_module = None

        # 3. Risk / Graph analysis engine
        try:
            import ai.risk as risk_mod  # type: ignore
            self._risk_module = risk_mod
            logger.info("Successfully bound Person 3 AI Risk engine.")
        except (ImportError, ModuleNotFoundError):
            self._risk_module = None

        # 4. Optimization solver
        try:
            import ai.optimization as opt_mod  # type: ignore
            self._optimization_module = opt_mod
            logger.info("Successfully bound Person 3 AI Optimization engine.")
        except (ImportError, ModuleNotFoundError):
            self._optimization_module = None

    def is_forecasting_available(self) -> bool:
        return self._forecast_module is not None

    def is_simulation_available(self) -> bool:
        return self._simulation_module is not None

    def is_risk_available(self) -> bool:
        return self._risk_module is not None

    def is_optimization_available(self) -> bool:
        return self._optimization_module is not None

    def get_status_summary(self) -> Dict[str, str]:
        """Returns the operational availability status of all AI/ML subsystems."""
        return {
            "forecasting": "ai_module_connected" if self.is_forecasting_available() else "service_fallback_active",
            "simulation": "ai_module_connected" if self.is_simulation_available() else "service_fallback_active",
            "risk_engine": "ai_module_connected" if self.is_risk_available() else "service_fallback_active",
            "optimization": "ai_module_connected" if self.is_optimization_available() else "service_fallback_active",
        }

    # Execution hooks
    def run_ai_forecast(self, **kwargs) -> Optional[Dict[str, Any]]:
        if not self._forecast_module:
            return None
        try:
            if hasattr(self._forecast_module, "predict"):
                return self._forecast_module.predict(**kwargs)
            elif hasattr(self._forecast_module, "forecast"):
                return self._forecast_module.forecast(**kwargs)
        except Exception as e:
            logger.warning(f"Error calling AI forecast module: {e}. Falling back to service adapter.")
        return None

    def run_ai_simulation(self, **kwargs) -> Optional[Dict[str, Any]]:
        if not self._simulation_module:
            return None
        try:
            if hasattr(self._simulation_module, "simulate"):
                return self._simulation_module.simulate(**kwargs)
            elif hasattr(self._simulation_module, "run_power_flow"):
                return self._simulation_module.run_power_flow(**kwargs)
        except Exception as e:
            logger.warning(f"Error calling AI simulation module: {e}. Falling back to service adapter.")
        return None

    def run_ai_risk_analysis(self, **kwargs) -> Optional[Dict[str, Any]]:
        if not self._risk_module:
            return None
        try:
            if hasattr(self._risk_module, "analyze"):
                return self._risk_module.analyze(**kwargs)
            elif hasattr(self._risk_module, "evaluate_risk"):
                return self._risk_module.evaluate_risk(**kwargs)
        except Exception as e:
            logger.warning(f"Error calling AI risk module: {e}. Falling back to service adapter.")
        return None

    def run_ai_optimization(self, **kwargs) -> Optional[Dict[str, Any]]:
        if not self._optimization_module:
            return None
        try:
            if hasattr(self._optimization_module, "optimize"):
                return self._optimization_module.optimize(**kwargs)
            elif hasattr(self._optimization_module, "solve_dispatch"):
                return self._optimization_module.solve_dispatch(**kwargs)
        except Exception as e:
            logger.warning(f"Error calling AI optimization module: {e}. Falling back to service adapter.")
        return None


ai_bridge = AIModuleBridge()
