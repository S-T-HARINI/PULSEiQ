"""
PULSEiQ - AI-Powered Electricity Grid Simulation, Risk Analysis & Optimization Platform.

Core AI/ML, Simulation, Graph, and Optimization Modules.
"""

from ai.models.grid import (
    ComponentStatus,
    CriticalityLevel,
    ElectricityGrid,
    GridNode,
    NodeType,
    OperationalData,
    RiskMetrics,
    ScenarioConfig,
    TransmissionLine,
)
from ai.models.mock_grid import create_mock_grid
from ai.forecasting import (
    DemandForecaster,
    GridForecaster,
    SolarForecaster,
    WindForecaster,
    ForecastResult,
    GridForecastSummary,
)
from ai.simulation import (
    SimulationResult,
    MonteCarloSummary,
    solve_power_flow,
    run_monte_carlo_simulation,
)
from ai.risk import (
    GridRiskAssessment,
    ContingencyResult,
    CascadingFailureReport,
    RiskLevel,
    run_n_1_analysis,
    run_n_k_analysis,
    simulate_cascading_failure,
    calculate_grid_risk_index,
)
from ai.graph import (
    grid_to_networkx,
    get_topology_summary,
    identify_important_nodes,
    find_connected_components,
    find_isolated_load_nodes,
)
from ai.optimization import (
    DispatchResult,
    OptimizationConfig,
    OptimizationStatus,
    solve_optimal_dispatch,
)

__version__ = "0.2.0"

__all__ = [
    # Grid Data Models
    "NodeType",
    "ComponentStatus",
    "CriticalityLevel",
    "OperationalData",
    "RiskMetrics",
    "GridNode",
    "TransmissionLine",
    "ScenarioConfig",
    "ElectricityGrid",
    "create_mock_grid",
    # Forecasting
    "DemandForecaster",
    "SolarForecaster",
    "WindForecaster",
    "GridForecaster",
    "ForecastResult",
    "GridForecastSummary",
    # Simulation
    "SimulationResult",
    "MonteCarloSummary",
    "solve_power_flow",
    "run_monte_carlo_simulation",
    # Risk Assessment
    "GridRiskAssessment",
    "ContingencyResult",
    "CascadingFailureReport",
    "RiskLevel",
    "run_n_1_analysis",
    "run_n_k_analysis",
    "simulate_cascading_failure",
    "calculate_grid_risk_index",
    # Graph Topology
    "grid_to_networkx",
    "get_topology_summary",
    "identify_important_nodes",
    "find_connected_components",
    "find_isolated_load_nodes",
    # Optimization
    "DispatchResult",
    "OptimizationConfig",
    "OptimizationStatus",
    "solve_optimal_dispatch",
]
