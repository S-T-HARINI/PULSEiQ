import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from ai.models.grid import (
    ComponentStatus as AIComponentStatus,
    CriticalityLevel as AICriticalityLevel,
    ElectricityGrid,
    GridNode as AIGridNode,
    NodeType as AINodeType,
    OperationalData as AIOperationalData,
    RiskMetrics as AIRiskMetrics,
    TransmissionLine as AITransmissionLine,
)
from backend.app.schemas.grid import (
    CustomGridCreate,
    CustomGridSummary,
    CustomGridUpdate,
    EdgeStatus,
    GridActivationResponse,
    GridDetailResponse,
    GridEdge,
    GridNode,
    GridNodePosition,
    GridResponse,
    GridSummary,
    NodeCriticality,
    NodeStatus,
    NodeType,
)


class GridService:
    """Service providing realistic electricity grid topology, asset states, and telemetry.
    Features an expansive 50-node enterprise digital twin network with 80+ interconnected
    multi-path transmission branches, meshed 400kV rings, BESS buffers, and dual-fed critical loads.
    Maintains an in-memory registry for the Reference Grid and user-created Custom Grids.
    """


    def __init__(self) -> None:
        self._nodes: List[GridNode] = [
            # =========================================================================
            # COLUMN 1: RENEWABLE GENERATION (8 Plants, X: 40)
            # =========================================================================
            GridNode(
                id="gen-solar-1",
                name="Helios Solar Alpha",
                type=NodeType.SOLAR_PLANT,
                capacity_mw=500.0,
                current_output_mw=480.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=96.0,
                risk_score=0.10,
                position=GridNodePosition(x=40.0, y=40.0),
                metadata={"irradiance_w_m2": 950.0, "inverter_status": "optimal"},
            ),
            GridNode(
                id="gen-solar-2",
                name="Helios Solar Beta",
                type=NodeType.SOLAR_PLANT,
                capacity_mw=450.0,
                current_output_mw=420.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=93.33,
                risk_score=0.11,
                position=GridNodePosition(x=40.0, y=180.0),
                metadata={"irradiance_w_m2": 930.0, "inverter_status": "optimal"},
            ),
            GridNode(
                id="gen-solar-3",
                name="Desert Sun PV 1",
                type=NodeType.SOLAR_PLANT,
                capacity_mw=400.0,
                current_output_mw=380.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=95.0,
                risk_score=0.09,
                position=GridNodePosition(x=40.0, y=320.0),
                metadata={"irradiance_w_m2": 960.0, "inverter_status": "optimal"},
            ),
            GridNode(
                id="gen-solar-4",
                name="Desert Sun PV 2",
                type=NodeType.SOLAR_PLANT,
                capacity_mw=350.0,
                current_output_mw=340.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=97.14,
                risk_score=0.08,
                position=GridNodePosition(x=40.0, y=460.0),
                metadata={"irradiance_w_m2": 940.0, "inverter_status": "optimal"},
            ),
            GridNode(
                id="gen-wind-1",
                name="Coastal Ridge Wind A",
                type=NodeType.WIND_PLANT,
                capacity_mw=550.0,
                current_output_mw=520.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=94.55,
                risk_score=0.14,
                position=GridNodePosition(x=40.0, y=600.0),
                metadata={"wind_speed_mps": 11.5, "turbine_count": 80},
            ),
            GridNode(
                id="gen-wind-2",
                name="Coastal Ridge Wind B",
                type=NodeType.WIND_PLANT,
                capacity_mw=500.0,
                current_output_mw=480.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=96.0,
                risk_score=0.13,
                position=GridNodePosition(x=40.0, y=740.0),
                metadata={"wind_speed_mps": 10.8, "turbine_count": 75},
            ),
            GridNode(
                id="gen-wind-3",
                name="Offshore Wind Alpha",
                type=NodeType.WIND_PLANT,
                capacity_mw=600.0,
                current_output_mw=580.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=96.67,
                risk_score=0.12,
                position=GridNodePosition(x=40.0, y=880.0),
                metadata={"wind_speed_mps": 12.8, "turbine_count": 90},
            ),
            GridNode(
                id="gen-wind-4",
                name="Offshore Wind Beta",
                type=NodeType.WIND_PLANT,
                capacity_mw=450.0,
                current_output_mw=420.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=93.33,
                risk_score=0.15,
                position=GridNodePosition(x=40.0, y=1020.0),
                metadata={"wind_speed_mps": 10.2, "turbine_count": 65},
            ),

            # =========================================================================
            # COLUMN 2: THERMAL, NUCLEAR & HYDRO BASE/PEAKING (8 Units, X: 340)
            # =========================================================================
            GridNode(
                id="gen-nuclear-1",
                name="Apex Nuclear Station",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=1200.0,
                current_output_mw=1100.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=91.67,
                risk_score=0.06,
                position=GridNodePosition(x=340.0, y=40.0),
                metadata={"fuel_type": "uranium", "reactor_status": "nominal", "heat_rate": 6400},
            ),
            GridNode(
                id="gen-gas-1",
                name="Metro Gas Combined 1",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=700.0,
                current_output_mw=650.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=92.86,
                risk_score=0.10,
                position=GridNodePosition(x=340.0, y=180.0),
                metadata={"fuel_type": "natural_gas", "ramp_rate_mw_min": 25.0},
            ),
            GridNode(
                id="gen-gas-2",
                name="Metro Gas Combined 2",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=600.0,
                current_output_mw=580.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=96.67,
                risk_score=0.09,
                position=GridNodePosition(x=340.0, y=320.0),
                metadata={"fuel_type": "natural_gas", "ramp_rate_mw_min": 25.0},
            ),
            GridNode(
                id="gen-hydro-1",
                name="Cascade Hydro Dam",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=500.0,
                current_output_mw=450.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.0,
                risk_score=0.08,
                position=GridNodePosition(x=340.0, y=460.0),
                metadata={"water_head_m": 145.0, "spinning_reserve_mw": 50.0},
            ),
            GridNode(
                id="gen-peaker-1",
                name="Fast Peaking Turbine A",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=350.0,
                current_output_mw=280.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=80.0,
                risk_score=0.16,
                position=GridNodePosition(x=340.0, y=600.0),
                metadata={"fast_start_sec": 180, "fuel_type": "gas_peaker"},
            ),
            GridNode(
                id="gen-peaker-2",
                name="Fast Peaking Turbine B",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=300.0,
                current_output_mw=260.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=86.67,
                risk_score=0.15,
                position=GridNodePosition(x=340.0, y=740.0),
                metadata={"fast_start_sec": 180, "fuel_type": "gas_peaker"},
            ),
            GridNode(
                id="gen-biomass-1",
                name="Valley Biomass Unit",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=150.0,
                current_output_mw=140.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.LOW,
                utilization_percent=93.33,
                risk_score=0.12,
                position=GridNodePosition(x=340.0, y=880.0),
                metadata={"fuel_type": "biomass", "carbon_offset_rate": 0.85},
            ),
            GridNode(
                id="gen-geothermal-1",
                name="Geothermal Base Plant",
                type=NodeType.CONVENTIONAL_GENERATOR,
                capacity_mw=200.0,
                current_output_mw=180.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=90.0,
                risk_score=0.07,
                position=GridNodePosition(x=340.0, y=1020.0),
                metadata={"steam_temp_c": 240.0, "availability": 0.99},
            ),

            # =========================================================================
            # COLUMN 3: STEP-UP HUBS & BESS STORAGE (8 Nodes, X: 640)
            # =========================================================================
            GridNode(
                id="sub-solar-stepup-1",
                name="Solar Step-Up Hub 1",
                type=NodeType.SUBSTATION,
                capacity_mw=1000.0,
                current_output_mw=900.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.0,
                risk_score=0.12,
                position=GridNodePosition(x=640.0, y=40.0),
                metadata={"voltage_kv": 400.0, "transformer_mva": 1200},
            ),
            GridNode(
                id="sub-solar-stepup-2",
                name="Solar Step-Up Hub 2",
                type=NodeType.SUBSTATION,
                capacity_mw=800.0,
                current_output_mw=720.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.0,
                risk_score=0.11,
                position=GridNodePosition(x=640.0, y=180.0),
                metadata={"voltage_kv": 400.0, "transformer_mva": 950},
            ),
            GridNode(
                id="sub-wind-stepup-1",
                name="Wind Step-Up Hub 1",
                type=NodeType.SUBSTATION,
                capacity_mw=1100.0,
                current_output_mw=1000.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.91,
                risk_score=0.13,
                position=GridNodePosition(x=640.0, y=320.0),
                metadata={"voltage_kv": 400.0, "transformer_mva": 1300},
            ),
            GridNode(
                id="sub-wind-stepup-2",
                name="Wind Step-Up Hub 2",
                type=NodeType.SUBSTATION,
                capacity_mw=1100.0,
                current_output_mw=1000.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.91,
                risk_score=0.14,
                position=GridNodePosition(x=640.0, y=460.0),
                metadata={"voltage_kv": 400.0, "transformer_mva": 1300},
            ),
            GridNode(
                id="bat-bess-1",
                name="Valley Grid Battery Storage (NeoStorage)",
                type=NodeType.BATTERY,
                capacity_mw=200.0,
                current_output_mw=180.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=90.0,
                risk_score=0.08,
                position=GridNodePosition(x=640.0, y=600.0),
                metadata={"capacity_mwh": 400.0, "state_of_charge_percent": 78.5, "mode": "discharging"},
            ),
            GridNode(
                id="bat-bess-2",
                name="GridReserve BESS 300MWh",
                type=NodeType.BATTERY,
                capacity_mw=150.0,
                current_output_mw=140.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=93.33,
                risk_score=0.07,
                position=GridNodePosition(x=640.0, y=740.0),
                metadata={"capacity_mwh": 300.0, "state_of_charge_percent": 91.2, "mode": "discharging"},
            ),
            GridNode(
                id="bat-bess-3",
                name="Apex BESS Fast Buffer",
                type=NodeType.BATTERY,
                capacity_mw=120.0,
                current_output_mw=95.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=79.17,
                risk_score=0.09,
                position=GridNodePosition(x=640.0, y=880.0),
                metadata={"capacity_mwh": 200.0, "state_of_charge_percent": 85.0, "mode": "standby"},
            ),
            GridNode(
                id="bat-bess-4",
                name="Highland BESS Stabilizer",
                type=NodeType.BATTERY,
                capacity_mw=100.0,
                current_output_mw=75.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=75.0,
                risk_score=0.08,
                position=GridNodePosition(x=640.0, y=1020.0),
                metadata={"capacity_mwh": 180.0, "state_of_charge_percent": 89.0, "mode": "regulating"},
            ),

            # =========================================================================
            # COLUMN 4: 400kV BULK TRANSMISSION HUBS & RING INTERTIES (10 Nodes, X: 960)
            # =========================================================================
            GridNode(
                id="sub-bulk-alpha",
                name="Bulk Substation Alpha 400kV (North Transmission)",
                type=NodeType.SUBSTATION,
                capacity_mw=2500.0,
                current_output_mw=2100.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=84.0,
                risk_score=0.15,
                position=GridNodePosition(x=960.0, y=40.0),
                metadata={"voltage_kv": 401.8, "bus_type": "slack_bus"},
            ),
            GridNode(
                id="sub-bulk-beta",
                name="Bulk Substation Beta 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=2200.0,
                current_output_mw=1950.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=88.64,
                risk_score=0.16,
                position=GridNodePosition(x=960.0, y=150.0),
                metadata={"voltage_kv": 400.9, "bus_type": "pv_bus"},
            ),
            GridNode(
                id="sub-bulk-gamma",
                name="Central Intertie Hub 400kV (Central Bulk)",
                type=NodeType.SUBSTATION,
                capacity_mw=2800.0,
                current_output_mw=2450.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=87.5,
                risk_score=0.18,
                position=GridNodePosition(x=960.0, y=260.0),
                metadata={"voltage_kv": 402.4, "bus_type": "pv_bus"},
            ),
            GridNode(
                id="sub-bulk-delta",
                name="South Bulk Hub 400kV (South Distribution)",
                type=NodeType.SUBSTATION,
                capacity_mw=2000.0,
                current_output_mw=1820.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=91.0,
                risk_score=0.17,
                position=GridNodePosition(x=960.0, y=370.0),
                metadata={"voltage_kv": 399.8, "bus_type": "pq_bus"},
            ),
            GridNode(
                id="sub-bulk-epsilon",
                name="Regional Ring Hub 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=2000.0,
                current_output_mw=1780.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=89.0,
                risk_score=0.14,
                position=GridNodePosition(x=960.0, y=480.0),
                metadata={"voltage_kv": 400.2, "bus_type": "pq_bus"},
            ),
            GridNode(
                id="sub-bulk-zeta",
                name="North Bulk Switching 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1800.0,
                current_output_mw=1550.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=86.11,
                risk_score=0.13,
                position=GridNodePosition(x=960.0, y=590.0),
                metadata={"voltage_kv": 401.1, "bus_type": "pq_bus"},
            ),
            GridNode(
                id="sub-intertie-east",
                name="East Grid Intertie 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1600.0,
                current_output_mw=1350.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=84.38,
                risk_score=0.12,
                position=GridNodePosition(x=960.0, y=700.0),
                metadata={"voltage_kv": 401.5, "bus_type": "tie_line"},
            ),
            GridNode(
                id="sub-intertie-west",
                name="West Grid Intertie 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1700.0,
                current_output_mw=1420.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=83.53,
                risk_score=0.11,
                position=GridNodePosition(x=960.0, y=810.0),
                metadata={"voltage_kv": 402.0, "bus_type": "tie_line"},
            ),
            GridNode(
                id="sub-crossborder",
                name="Cross-Border Tie 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1500.0,
                current_output_mw=1250.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=83.33,
                risk_score=0.10,
                position=GridNodePosition(x=960.0, y=920.0),
                metadata={"voltage_kv": 400.6, "bus_type": "tie_line"},
            ),
            GridNode(
                id="sub-ring-master",
                name="Central Ring Master 400kV",
                type=NodeType.SUBSTATION,
                capacity_mw=2600.0,
                current_output_mw=2200.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=84.62,
                risk_score=0.15,
                position=GridNodePosition(x=960.0, y=1030.0),
                metadata={"voltage_kv": 402.2, "bus_type": "ring_master"},
            ),

            # =========================================================================
            # COLUMN 5: 220kV / 132kV DISTRIBUTION SUBSTATIONS (8 Nodes, X: 1280)
            # =========================================================================
            GridNode(
                id="sub-dist-metro-1",
                name="Metro Step-Down 220kV A",
                type=NodeType.SUBSTATION,
                capacity_mw=1600.0,
                current_output_mw=1480.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=92.5,
                risk_score=0.15,
                position=GridNodePosition(x=1280.0, y=40.0),
                metadata={"voltage_kv": 220.5, "busbar_status": "balanced"},
            ),
            GridNode(
                id="sub-dist-metro-2",
                name="Metro Step-Down 220kV B",
                type=NodeType.SUBSTATION,
                capacity_mw=1200.0,
                current_output_mw=1050.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=87.5,
                risk_score=0.13,
                position=GridNodePosition(x=1280.0, y=180.0),
                metadata={"voltage_kv": 220.0, "busbar_status": "balanced"},
            ),
            GridNode(
                id="sub-dist-urban-n",
                name="North Urban Feeder 132kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1100.0,
                current_output_mw=980.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=89.09,
                risk_score=0.14,
                position=GridNodePosition(x=1280.0, y=320.0),
                metadata={"voltage_kv": 132.2, "feeder_count": 8},
            ),
            GridNode(
                id="sub-dist-urban-s",
                name="South Suburban Feeder 132kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1000.0,
                current_output_mw=890.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=89.0,
                risk_score=0.12,
                position=GridNodePosition(x=1280.0, y=460.0),
                metadata={"voltage_kv": 132.0, "feeder_count": 6},
            ),
            GridNode(
                id="sub-dist-ind-1",
                name="Heavy Industrial Sub 220kV",
                type=NodeType.SUBSTATION,
                capacity_mw=1300.0,
                current_output_mw=1120.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=86.15,
                risk_score=0.16,
                position=GridNodePosition(x=1280.0, y=600.0),
                metadata={"voltage_kv": 220.1, "reactive_compensation": "SVC_active"},
            ),
            GridNode(
                id="sub-dist-tech",
                name="Tech Corridor Sub 132kV",
                type=NodeType.SUBSTATION,
                capacity_mw=900.0,
                current_output_mw=760.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=84.44,
                risk_score=0.11,
                position=GridNodePosition(x=1280.0, y=740.0),
                metadata={"voltage_kv": 132.4, "power_quality_thd": 1.2},
            ),
            GridNode(
                id="sub-dist-harbor",
                name="Harbor Logistics Sub 132kV",
                type=NodeType.SUBSTATION,
                capacity_mw=950.0,
                current_output_mw=840.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=88.42,
                risk_score=0.13,
                position=GridNodePosition(x=1280.0, y=880.0),
                metadata={"voltage_kv": 132.1, "crane_inrush_damping": True},
            ),
            GridNode(
                id="sub-dist-airport",
                name="Transit & Airport Sub 132kV",
                type=NodeType.SUBSTATION,
                capacity_mw=850.0,
                current_output_mw=720.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=84.71,
                risk_score=0.10,
                position=GridNodePosition(x=1280.0, y=1020.0),
                metadata={"voltage_kv": 132.5, "traction_rectifier_filter": True},
            ),

            # =========================================================================
            # COLUMN 6: URBAN LOAD SINKS & CRITICAL FACILITIES (8 Nodes, X: 1600)
            # =========================================================================
            GridNode(
                id="load-hospital-metro",
                name="Metro University Hospital & Trauma Center",
                type=NodeType.CRITICAL_LOAD,
                capacity_mw=100.0,
                current_output_mw=45.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=45.0,
                risk_score=0.05,
                position=GridNodePosition(x=1600.0, y=40.0),
                metadata={"dual_feed_active": True, "backup_generators": 4, "priority": "Tier-1"},
            ),
            GridNode(
                id="load-hospital-north",
                name="North Regional General Hospital",
                type=NodeType.CRITICAL_LOAD,
                capacity_mw=80.0,
                current_output_mw=65.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=81.25,
                risk_score=0.06,
                position=GridNodePosition(x=1600.0, y=180.0),
                metadata={"dual_feed_active": True, "backup_generators": 3, "priority": "Tier-1"},
            ),
            GridNode(
                id="load-datacenter-cloud",
                name="Financial Cloud Data Center",
                type=NodeType.CRITICAL_LOAD,
                capacity_mw=400.0,
                current_output_mw=340.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=85.0,
                risk_score=0.07,
                position=GridNodePosition(x=1600.0, y=320.0),
                metadata={"dual_feed_active": True, "ups_reserve_min": 60, "priority": "Tier-1"},
            ),
            GridNode(
                id="load-ai-supercluster",
                name="AI GPU Training Supercluster",
                type=NodeType.CRITICAL_LOAD,
                capacity_mw=500.0,
                current_output_mw=420.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.CRITICAL,
                utilization_percent=84.0,
                risk_score=0.08,
                position=GridNodePosition(x=1600.0, y=460.0),
                metadata={"h100_cluster_load": True, "cooling_pue": 1.12, "priority": "Tier-1"},
            ),
            GridNode(
                id="load-city-cbd",
                name="Downtown Financial Center (Metro Central CBD)",
                type=NodeType.LOAD,
                capacity_mw=1300.0,
                current_output_mw=1140.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=87.69,
                risk_score=0.12,
                position=GridNodePosition(x=1600.0, y=600.0),
                metadata={"commercial_density": "high", "sheddable": False},
            ),
            GridNode(
                id="load-industrial-heavy",
                name="East Harbor Industrial Zone (Heavy Manufacturing)",
                type=NodeType.LOAD,
                capacity_mw=900.0,
                current_output_mw=780.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.MEDIUM,
                utilization_percent=86.67,
                risk_score=0.15,
                position=GridNodePosition(x=1600.0, y=740.0),
                metadata={"arc_furnace_present": True, "sheddable": True},
            ),
            GridNode(
                id="load-residential-metro",
                name="Metro Heights Residential District",
                type=NodeType.LOAD,
                capacity_mw=600.0,
                current_output_mw=520.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.LOW,
                utilization_percent=86.67,
                risk_score=0.10,
                position=GridNodePosition(x=1600.0, y=880.0),
                metadata={"smart_meters": 124000, "ev_chargers": 8500},
            ),
            GridNode(
                id="load-transit-rail",
                name="High-Speed Rail & Port Terminal",
                type=NodeType.LOAD,
                capacity_mw=450.0,
                current_output_mw=390.0,
                status=NodeStatus.ONLINE,
                criticality=NodeCriticality.HIGH,
                utilization_percent=86.67,
                risk_score=0.11,
                position=GridNodePosition(x=1600.0, y=1020.0),
                metadata={"traction_substations": 6, "container_cranes": 28},
            ),
        ]

        # =========================================================================
        # 80+ INTERCONNECTED TRANSMISSION LINES (MULTI-PATH MESH NETWORK)
        # =========================================================================
        self._edges: List[GridEdge] = [
            # --- Col 1 (Solar/Wind) -> Col 3 (Step-Up Hubs) ---
            GridEdge(id="line-solar-to-north", source="gen-solar-1", target="sub-solar-stepup-1", capacity_mw=600.0, power_flow_mw=480.0, utilization_percent=80.0, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.02, reactance_ohms=0.10),
            GridEdge(id="e-s2-su1", source="gen-solar-2", target="sub-solar-stepup-1", capacity_mw=550.0, power_flow_mw=420.0, utilization_percent=76.36, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.02, reactance_ohms=0.10),
            GridEdge(id="e-s3-su2", source="gen-solar-3", target="sub-solar-stepup-2", capacity_mw=500.0, power_flow_mw=380.0, utilization_percent=76.0, status=EdgeStatus.NORMAL, risk_score=0.09, resistance_ohms=0.025, reactance_ohms=0.12),
            GridEdge(id="e-s4-su2", source="gen-solar-4", target="sub-solar-stepup-2", capacity_mw=450.0, power_flow_mw=340.0, utilization_percent=75.56, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.025, reactance_ohms=0.12),
            GridEdge(id="line-wind-to-central", source="gen-wind-1", target="sub-wind-stepup-1", capacity_mw=650.0, power_flow_mw=520.0, utilization_percent=80.0, status=EdgeStatus.NORMAL, risk_score=0.14, resistance_ohms=0.02, reactance_ohms=0.11),
            GridEdge(id="e-w2-wu1", source="gen-wind-2", target="sub-wind-stepup-1", capacity_mw=600.0, power_flow_mw=480.0, utilization_percent=80.0, status=EdgeStatus.NORMAL, risk_score=0.13, resistance_ohms=0.02, reactance_ohms=0.11),
            GridEdge(id="e-w3-wu2", source="gen-wind-3", target="sub-wind-stepup-2", capacity_mw=700.0, power_flow_mw=580.0, utilization_percent=82.86, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.018, reactance_ohms=0.09),
            GridEdge(id="e-w4-wu2", source="gen-wind-4", target="sub-wind-stepup-2", capacity_mw=550.0, power_flow_mw=420.0, utilization_percent=76.36, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.022, reactance_ohms=0.12),

            # --- Col 1 cross-ties to thermal hubs ---
            GridEdge(id="e-s2-th1", source="gen-solar-2", target="gen-gas-1", capacity_mw=300.0, power_flow_mw=120.0, utilization_percent=40.0, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.03, reactance_ohms=0.15),
            GridEdge(id="e-w2-th2", source="gen-wind-2", target="gen-hydro-1", capacity_mw=350.0, power_flow_mw=150.0, utilization_percent=42.86, status=EdgeStatus.NORMAL, risk_score=0.09, resistance_ohms=0.03, reactance_ohms=0.15),

            # --- Col 2 (Base/Peakers) -> Col 4 (400kV Bulk Hubs) ---
            GridEdge(id="e-nuc-alpha", source="gen-nuclear-1", target="sub-bulk-alpha", capacity_mw=1400.0, power_flow_mw=1100.0, utilization_percent=78.57, status=EdgeStatus.NORMAL, risk_score=0.06, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="line-gas-to-north", source="gen-gas-1", target="sub-bulk-beta", capacity_mw=850.0, power_flow_mw=650.0, utilization_percent=76.47, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.015, reactance_ohms=0.08),
            GridEdge(id="e-gas2-gamma", source="gen-gas-2", target="sub-bulk-gamma", capacity_mw=750.0, power_flow_mw=580.0, utilization_percent=77.33, status=EdgeStatus.NORMAL, risk_score=0.09, resistance_ohms=0.016, reactance_ohms=0.08),
            GridEdge(id="e-hydro-delta", source="gen-hydro-1", target="sub-bulk-delta", capacity_mw=650.0, power_flow_mw=450.0, utilization_percent=69.23, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.018, reactance_ohms=0.09),
            GridEdge(id="e-peak1-eps", source="gen-peaker-1", target="sub-bulk-epsilon", capacity_mw=450.0, power_flow_mw=280.0, utilization_percent=62.22, status=EdgeStatus.NORMAL, risk_score=0.16, resistance_ohms=0.024, reactance_ohms=0.12),
            GridEdge(id="e-peak2-zeta", source="gen-peaker-2", target="sub-bulk-zeta", capacity_mw=400.0, power_flow_mw=260.0, utilization_percent=65.0, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.025, reactance_ohms=0.13),
            GridEdge(id="e-bio-east", source="gen-biomass-1", target="sub-intertie-east", capacity_mw=200.0, power_flow_mw=140.0, utilization_percent=70.0, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.035, reactance_ohms=0.18),
            GridEdge(id="e-geo-west", source="gen-geothermal-1", target="sub-intertie-west", capacity_mw=250.0, power_flow_mw=180.0, utilization_percent=72.0, status=EdgeStatus.NORMAL, risk_score=0.07, resistance_ohms=0.030, reactance_ohms=0.15),

            # --- Col 3 (Step-Up & BESS) -> Col 4 (400kV Bulk Hubs) ---
            GridEdge(id="e-su1-ba", source="sub-solar-stepup-1", target="sub-bulk-alpha", capacity_mw=1200.0, power_flow_mw=900.0, utilization_percent=75.0, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.015, reactance_ohms=0.07),
            GridEdge(id="e-su2-bb", source="sub-solar-stepup-2", target="sub-bulk-beta", capacity_mw=1000.0, power_flow_mw=720.0, utilization_percent=72.0, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.016, reactance_ohms=0.08),
            GridEdge(id="e-wu1-bg", source="sub-wind-stepup-1", target="sub-bulk-gamma", capacity_mw=1300.0, power_flow_mw=1000.0, utilization_percent=76.92, status=EdgeStatus.NORMAL, risk_score=0.13, resistance_ohms=0.014, reactance_ohms=0.07),
            GridEdge(id="e-wu2-bd", source="sub-wind-stepup-2", target="sub-bulk-delta", capacity_mw=1300.0, power_flow_mw=1000.0, utilization_percent=76.92, status=EdgeStatus.NORMAL, risk_score=0.14, resistance_ohms=0.014, reactance_ohms=0.07),
            GridEdge(id="line-bess-to-north", source="bat-bess-1", target="sub-bulk-epsilon", capacity_mw=300.0, power_flow_mw=180.0, utilization_percent=60.0, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.02, reactance_ohms=0.10),
            GridEdge(id="e-b2-bz", source="bat-bess-2", target="sub-bulk-zeta", capacity_mw=250.0, power_flow_mw=140.0, utilization_percent=56.0, status=EdgeStatus.NORMAL, risk_score=0.07, resistance_ohms=0.022, reactance_ohms=0.11),
            GridEdge(id="e-b3-ie", source="bat-bess-3", target="sub-intertie-east", capacity_mw=200.0, power_flow_mw=95.0, utilization_percent=47.5, status=EdgeStatus.NORMAL, risk_score=0.09, resistance_ohms=0.025, reactance_ohms=0.13),
            GridEdge(id="e-b4-iw", source="bat-bess-4", target="sub-intertie-west", capacity_mw=180.0, power_flow_mw=75.0, utilization_percent=41.67, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.028, reactance_ohms=0.14),

            # --- 400kV Bulk Inter-Hub Meshed Ring Network (Loops & Redundancies) ---
            GridEdge(id="line-north-central-1", source="sub-bulk-alpha", target="sub-bulk-beta", capacity_mw=1500.0, power_flow_mw=850.0, utilization_percent=56.67, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.010, reactance_ohms=0.05),
            GridEdge(id="e-bb-bg", source="sub-bulk-beta", target="sub-bulk-gamma", capacity_mw=1600.0, power_flow_mw=920.0, utilization_percent=57.5, status=EdgeStatus.NORMAL, risk_score=0.16, resistance_ohms=0.010, reactance_ohms=0.05),
            GridEdge(id="line-central-south-1", source="sub-bulk-gamma", target="sub-bulk-delta", capacity_mw=1800.0, power_flow_mw=1140.0, utilization_percent=63.33, status=EdgeStatus.NORMAL, risk_score=0.18, resistance_ohms=0.009, reactance_ohms=0.045),
            GridEdge(id="e-bd-be", source="sub-bulk-delta", target="sub-bulk-epsilon", capacity_mw=1500.0, power_flow_mw=980.0, utilization_percent=65.33, status=EdgeStatus.NORMAL, risk_score=0.17, resistance_ohms=0.011, reactance_ohms=0.055),
            GridEdge(id="e-be-bz", source="sub-bulk-epsilon", target="sub-bulk-zeta", capacity_mw=1400.0, power_flow_mw=840.0, utilization_percent=60.0, status=EdgeStatus.NORMAL, risk_score=0.14, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="e-bz-ie", source="sub-bulk-zeta", target="sub-intertie-east", capacity_mw=1300.0, power_flow_mw=790.0, utilization_percent=60.77, status=EdgeStatus.NORMAL, risk_score=0.13, resistance_ohms=0.013, reactance_ohms=0.065),
            GridEdge(id="e-ie-iw", source="sub-intertie-east", target="sub-intertie-west", capacity_mw=1400.0, power_flow_mw=860.0, utilization_percent=61.43, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="e-iw-cb", source="sub-intertie-west", target="sub-crossborder", capacity_mw=1200.0, power_flow_mw=720.0, utilization_percent=60.0, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.014, reactance_ohms=0.07),
            GridEdge(id="e-cb-rm", source="sub-crossborder", target="sub-ring-master", capacity_mw=1500.0, power_flow_mw=950.0, utilization_percent=63.33, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.010, reactance_ohms=0.05),
            GridEdge(id="e-rm-ba", source="sub-ring-master", target="sub-bulk-alpha", capacity_mw=1800.0, power_flow_mw=1180.0, utilization_percent=65.56, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.009, reactance_ohms=0.045),

            # Cross-tie Diagonal Trunk Lines for N-1 Robustness
            GridEdge(id="e-ba-bg", source="sub-bulk-alpha", target="sub-bulk-gamma", capacity_mw=1200.0, power_flow_mw=680.0, utilization_percent=56.67, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="e-bb-bd", source="sub-bulk-beta", target="sub-bulk-delta", capacity_mw=1200.0, power_flow_mw=640.0, utilization_percent=53.33, status=EdgeStatus.NORMAL, risk_score=0.16, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="e-bg-be", source="sub-bulk-gamma", target="sub-bulk-epsilon", capacity_mw=1300.0, power_flow_mw=720.0, utilization_percent=55.38, status=EdgeStatus.NORMAL, risk_score=0.18, resistance_ohms=0.011, reactance_ohms=0.055),
            GridEdge(id="e-bd-bz", source="sub-bulk-delta", target="sub-bulk-zeta", capacity_mw=1100.0, power_flow_mw=590.0, utilization_percent=53.64, status=EdgeStatus.NORMAL, risk_score=0.17, resistance_ohms=0.013, reactance_ohms=0.065),

            # --- Col 4 (400kV Bulk) -> Col 5 (Distribution Substations 220kV/132kV) ---
            GridEdge(id="e-ba-d1", source="sub-bulk-alpha", target="sub-dist-metro-1", capacity_mw=1800.0, power_flow_mw=1480.0, utilization_percent=82.22, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.015, reactance_ohms=0.075),
            GridEdge(id="e-bb-d2", source="sub-bulk-beta", target="sub-dist-metro-2", capacity_mw=1400.0, power_flow_mw=1050.0, utilization_percent=75.0, status=EdgeStatus.NORMAL, risk_score=0.13, resistance_ohms=0.018, reactance_ohms=0.09),
            GridEdge(id="e-bg-dn", source="sub-bulk-gamma", target="sub-dist-urban-n", capacity_mw=1200.0, power_flow_mw=980.0, utilization_percent=81.67, status=EdgeStatus.NORMAL, risk_score=0.14, resistance_ohms=0.020, reactance_ohms=0.10),
            GridEdge(id="e-bd-ds", source="sub-bulk-delta", target="sub-dist-urban-s", capacity_mw=1100.0, power_flow_mw=890.0, utilization_percent=80.91, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.022, reactance_ohms=0.11),
            GridEdge(id="e-be-di", source="sub-bulk-epsilon", target="sub-dist-ind-1", capacity_mw=1400.0, power_flow_mw=1120.0, utilization_percent=80.0, status=EdgeStatus.NORMAL, risk_score=0.16, resistance_ohms=0.017, reactance_ohms=0.085),
            GridEdge(id="e-bz-dt", source="sub-bulk-zeta", target="sub-dist-tech", capacity_mw=1000.0, power_flow_mw=760.0, utilization_percent=76.0, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.024, reactance_ohms=0.12),
            GridEdge(id="e-ie-dh", source="sub-intertie-east", target="sub-dist-harbor", capacity_mw=1100.0, power_flow_mw=840.0, utilization_percent=76.36, status=EdgeStatus.NORMAL, risk_score=0.13, resistance_ohms=0.022, reactance_ohms=0.11),
            GridEdge(id="e-iw-da", source="sub-intertie-west", target="sub-dist-airport", capacity_mw=950.0, power_flow_mw=720.0, utilization_percent=75.79, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.026, reactance_ohms=0.13),

            # Distribution Ring Cross-Ties (Inter-substation loops)
            GridEdge(id="e-d1-d2", source="sub-dist-metro-1", target="sub-dist-metro-2", capacity_mw=600.0, power_flow_mw=280.0, utilization_percent=46.67, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.03, reactance_ohms=0.15),
            GridEdge(id="e-dn-ds", source="sub-dist-urban-n", target="sub-dist-urban-s", capacity_mw=500.0, power_flow_mw=220.0, utilization_percent=44.0, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.035, reactance_ohms=0.17),
            GridEdge(id="e-di-dt", source="sub-dist-ind-1", target="sub-dist-tech", capacity_mw=650.0, power_flow_mw=310.0, utilization_percent=47.69, status=EdgeStatus.NORMAL, risk_score=0.14, resistance_ohms=0.028, reactance_ohms=0.14),
            GridEdge(id="e-dh-da", source="sub-dist-harbor", target="sub-dist-airport", capacity_mw=550.0, power_flow_mw=250.0, utilization_percent=45.45, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.032, reactance_ohms=0.16),

            # --- Col 5 (Distribution) -> Col 6 (Critical & Urban Load Sinks) ---
            # Critical Hospital Feed (Single radial high-priority feeder)
            GridEdge(id="line-south-to-hospital", source="sub-dist-metro-1", target="load-hospital-metro", capacity_mw=120.0, power_flow_mw=45.0, utilization_percent=37.5, status=EdgeStatus.NORMAL, risk_score=0.05, resistance_ohms=0.015, reactance_ohms=0.075),

            GridEdge(id="e-dn-hosp2-primary", source="sub-dist-urban-n", target="load-hospital-north", capacity_mw=90.0, power_flow_mw=65.0, utilization_percent=72.22, status=EdgeStatus.NORMAL, risk_score=0.06, resistance_ohms=0.020, reactance_ohms=0.10),
            GridEdge(id="e-d1-hosp2-backup", source="sub-dist-metro-1", target="load-hospital-north", capacity_mw=80.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.06, resistance_ohms=0.022, reactance_ohms=0.11),

            # Dual-Fed Cloud Data Center & AI GPU Supercluster
            GridEdge(id="e-dt-dc-primary", source="sub-dist-tech", target="load-datacenter-cloud", capacity_mw=450.0, power_flow_mw=340.0, utilization_percent=75.56, status=EdgeStatus.NORMAL, risk_score=0.07, resistance_ohms=0.012, reactance_ohms=0.06),
            GridEdge(id="e-d2-dc-backup", source="sub-dist-metro-2", target="load-datacenter-cloud", capacity_mw=400.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.07, resistance_ohms=0.014, reactance_ohms=0.07),

            GridEdge(id="e-dt-ai-primary", source="sub-dist-tech", target="load-ai-supercluster", capacity_mw=550.0, power_flow_mw=420.0, utilization_percent=76.36, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.010, reactance_ohms=0.05),
            GridEdge(id="e-di-ai-backup", source="sub-dist-ind-1", target="load-ai-supercluster", capacity_mw=500.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.08, resistance_ohms=0.012, reactance_ohms=0.06),

            # Commercial CBD, Industrial & Residential Feeds
            GridEdge(id="line-central-to-commercial", source="sub-dist-metro-1", target="load-city-cbd", capacity_mw=1400.0, power_flow_mw=1140.0, utilization_percent=81.43, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.008, reactance_ohms=0.04),
            GridEdge(id="e-d2-cbd", source="sub-dist-metro-2", target="load-city-cbd", capacity_mw=800.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.12, resistance_ohms=0.012, reactance_ohms=0.06),

            GridEdge(id="line-central-to-industrial", source="sub-dist-ind-1", target="load-industrial-heavy", capacity_mw=1000.0, power_flow_mw=780.0, utilization_percent=78.0, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.010, reactance_ohms=0.05),
            GridEdge(id="e-dh-ind", source="sub-dist-harbor", target="load-industrial-heavy", capacity_mw=600.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.15, resistance_ohms=0.015, reactance_ohms=0.075),

            GridEdge(id="line-north-to-residential", source="sub-dist-urban-s", target="load-residential-metro", capacity_mw=700.0, power_flow_mw=520.0, utilization_percent=74.29, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.014, reactance_ohms=0.07),
            GridEdge(id="e-dn-res", source="sub-dist-urban-n", target="load-residential-metro", capacity_mw=500.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.10, resistance_ohms=0.018, reactance_ohms=0.09),

            GridEdge(id="e-da-rail", source="sub-dist-airport", target="load-transit-rail", capacity_mw=550.0, power_flow_mw=390.0, utilization_percent=70.91, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.016, reactance_ohms=0.08),
            GridEdge(id="e-dh-rail", source="sub-dist-harbor", target="load-transit-rail", capacity_mw=500.0, power_flow_mw=0.0, utilization_percent=0.0, status=EdgeStatus.NORMAL, risk_score=0.11, resistance_ohms=0.018, reactance_ohms=0.09),
        ]
        self._reference_grid_id: str = "reference_demo_grid"
        self._active_grid_id: str = "reference_demo_grid"
        self._reference_name: str = "PULSEiQ Regional Demonstration Grid"
        self._reference_description: str = "A regional 400kV/220kV/132kV bulk transmission digital twin network featuring mixed generation, renewable sources, storage, and critical loads."
        self._custom_grids: Dict[str, ElectricityGrid] = {}
        self._custom_grid_metadata: Dict[str, Dict[str, Any]] = {}

    def get_active_grid_id(self) -> str:
        """Returns the ID of the currently active grid."""
        return self._active_grid_id

    def get_reference_grid(self) -> ElectricityGrid:
        """Constructs an ElectricityGrid representation of the Reference Grid."""
        from backend.app.core.ai_bridge import ai_bridge
        ref_state = self._get_reference_grid_state()
        eg = ai_bridge.convert_to_ai_grid(ref_state)
        eg.grid_id = self._reference_grid_id
        eg.name = self._reference_name
        eg.description = self._reference_description
        return eg

    def get_active_grid(self) -> ElectricityGrid:
        """Returns the currently active ElectricityGrid instance."""
        if self._active_grid_id == self._reference_grid_id:
            return self.get_reference_grid()
        if self._active_grid_id in self._custom_grids:
            return self._custom_grids[self._active_grid_id]
        return self.get_reference_grid()

    def set_active_grid(self, grid_id: str) -> GridActivationResponse:
        """Selects and activates a specific grid (reference or custom)."""
        if grid_id == self._reference_grid_id or grid_id == "pulseiq-digital-twin":
            self._active_grid_id = self._reference_grid_id
            return GridActivationResponse(
                status="activated",
                active_grid_id=self._reference_grid_id,
                active_grid_name=self._reference_name,
                is_reference=True,
                message=f"Reference grid '{self._reference_name}' is now active.",
            )

        if grid_id not in self._custom_grids:
            raise KeyError(f"Grid with ID '{grid_id}' not found in registry.")

        self._active_grid_id = grid_id
        cg = self._custom_grids[grid_id]
        return GridActivationResponse(
            status="activated",
            active_grid_id=cg.grid_id,
            active_grid_name=cg.name,
            is_reference=False,
            message=f"Custom grid '{cg.name}' ({cg.grid_id}) is now active.",
        )

    def _get_reference_grid_state(self) -> GridResponse:
        """Calculates and returns the reference demo grid state."""
        total_generation = 0.0
        renewable_generation = 0.0
        total_demand = 0.0

        for node in self._nodes:
            if node.type in (NodeType.CONVENTIONAL_GENERATOR, NodeType.SOLAR_PLANT, NodeType.WIND_PLANT):
                if node.status == NodeStatus.ONLINE:
                    total_generation += node.current_output_mw
                    if node.type in (NodeType.SOLAR_PLANT, NodeType.WIND_PLANT):
                        renewable_generation += node.current_output_mw
            elif node.type == NodeType.BATTERY:
                if node.status == NodeStatus.ONLINE and node.current_output_mw > 0:
                    total_generation += node.current_output_mw
            elif node.type in (NodeType.LOAD, NodeType.CRITICAL_LOAD):
                if node.status == NodeStatus.ONLINE:
                    total_demand += node.current_output_mw

        renewable_percentage = (
            round((renewable_generation / total_generation) * 100, 2)
            if total_generation > 0
            else 0.0
        )

        battery_node = next((n for n in self._nodes if n.type == NodeType.BATTERY), None)
        battery_soc = (
            battery_node.metadata.get("state_of_charge_percent", 78.5)
            if battery_node
            else 0.0
        )

        active_contingencies = sum(1 for e in self._edges if e.status != EdgeStatus.NORMAL) + sum(
            1 for n in self._nodes if n.status != NodeStatus.ONLINE
        )
        grid_risk_index = round(0.12 + (0.08 * active_contingencies), 4)

        summary = GridSummary(
            total_generation_mw=round(total_generation, 2),
            total_demand_mw=round(total_demand, 2),
            renewable_percentage=renewable_percentage,
            battery_soc=battery_soc,
            grid_risk_index=min(1.0, grid_risk_index),
            active_contingencies_count=active_contingencies,
            net_power_balance_mw=round(total_generation - total_demand, 2),
        )

        return GridResponse(
            grid_id=self._reference_grid_id,
            name=self._reference_name,
            is_reference=True,
            is_active=(self._active_grid_id == self._reference_grid_id),
            nodes=self._nodes,
            edges=self._edges,
            summary=summary,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _convert_custom_grid_to_grid_response(self, cg: ElectricityGrid) -> GridResponse:
        """Converts an ElectricityGrid instance to standard GridResponse format."""
        detail = self._electricity_grid_to_pydantic(
            cg,
            is_active=(self._active_grid_id == cg.grid_id),
            is_reference=False,
        )
        return GridResponse(
            grid_id=cg.grid_id,
            name=cg.name,
            is_reference=False,
            is_active=(self._active_grid_id == cg.grid_id),
            nodes=detail.nodes,
            edges=detail.edges,
            summary=detail.summary,
            timestamp=detail.timestamp,
        )

    def get_grid_state(self, grid_id: Optional[str] = None) -> GridResponse:
        """
        Calculates and returns grid state and summary metrics for the active
        or specified grid ID.
        """
        target_id = grid_id or self._active_grid_id

        if target_id == self._reference_grid_id or target_id == "pulseiq-digital-twin":
            return self._get_reference_grid_state()

        if target_id in self._custom_grids:
            return self._convert_custom_grid_to_grid_response(self._custom_grids[target_id])

        return self._get_reference_grid_state()

    def create_custom_grid(self, grid_data: CustomGridCreate) -> GridDetailResponse:
        """
        Registers a new custom electricity grid in the in-memory registry.
        Performs full topological validation using ElectricityGrid.validate_grid().
        """
        gid = grid_data.grid_id or f"custom_grid_{uuid.uuid4().hex[:8]}"

        if gid == self._reference_grid_id:
            raise ValueError(f"Grid ID '{self._reference_grid_id}' is reserved for the Reference Demo Grid.")

        if gid in self._custom_grids:
            raise ValueError(f"Custom grid with ID '{gid}' already exists.")

        eg = self._pydantic_to_electricity_grid(grid_data, grid_id=gid)

        validation_errors = eg.validate_grid()
        if validation_errors:
            raise ValueError(f"Topological validation failed: {'; '.join(validation_errors)}")

        now_iso = datetime.now(timezone.utc).isoformat()
        self._custom_grids[gid] = eg
        self._custom_grid_metadata[gid] = {
            "created_at": now_iso,
            "updated_at": now_iso,
        }

        return self._electricity_grid_to_pydantic(
            eg,
            is_active=(self._active_grid_id == gid),
            is_reference=False,
        )

    def list_grids(self) -> List[CustomGridSummary]:
        """Lists summaries of all available reference and custom grids."""
        ref_state = self._get_reference_grid_state()
        summaries: List[CustomGridSummary] = [
            CustomGridSummary(
                grid_id=self._reference_grid_id,
                name=self._reference_name,
                description=self._reference_description,
                is_reference=True,
                is_active=(self._active_grid_id == self._reference_grid_id),
                node_count=len(self._nodes),
                edge_count=len(self._edges),
                total_generation_mw=ref_state.summary.total_generation_mw,
                total_demand_mw=ref_state.summary.total_demand_mw,
                created_at="2026-01-01T00:00:00Z",
                updated_at="2026-01-01T00:00:00Z",
            )
        ]

        for gid, cg in self._custom_grids.items():
            meta = self._custom_grid_metadata.get(gid, {})
            summaries.append(
                CustomGridSummary(
                    grid_id=cg.grid_id,
                    name=cg.name,
                    description=cg.description,
                    is_reference=False,
                    is_active=(self._active_grid_id == cg.grid_id),
                    node_count=len(cg.nodes),
                    edge_count=len(cg.lines),
                    total_generation_mw=round(cg.total_generation_mw, 2),
                    total_demand_mw=round(cg.total_demand_mw, 2),
                    created_at=meta.get("created_at"),
                    updated_at=meta.get("updated_at"),
                )
            )

        return summaries

    def get_grid_detail(self, grid_id: str) -> Optional[GridDetailResponse]:
        """Retrieves full topological and operational details for a grid by ID."""
        if grid_id == self._reference_grid_id or grid_id == "pulseiq-digital-twin":
            ref_eg = self.get_reference_grid()
            return self._electricity_grid_to_pydantic(
                ref_eg,
                is_active=(self._active_grid_id == self._reference_grid_id),
                is_reference=True,
            )

        if grid_id in self._custom_grids:
            cg = self._custom_grids[grid_id]
            return self._electricity_grid_to_pydantic(
                cg,
                is_active=(self._active_grid_id == grid_id),
                is_reference=False,
            )

        return None

    def update_custom_grid(self, grid_id: str, update_data: CustomGridUpdate) -> GridDetailResponse:
        """Updates an existing custom grid topology and metadata."""
        if grid_id == self._reference_grid_id or grid_id == "pulseiq-digital-twin":
            raise ValueError("Reference demonstration grid is immutable and cannot be updated.")

        if grid_id not in self._custom_grids:
            raise KeyError(f"Custom grid with ID '{grid_id}' not found.")

        existing_grid = self._custom_grids[grid_id]

        new_name = update_data.name if update_data.name is not None else existing_grid.name
        new_desc = update_data.description if update_data.description is not None else existing_grid.description
        new_meta = dict(existing_grid.metadata)
        if update_data.metadata is not None:
            new_meta.update(update_data.metadata)

        if update_data.nodes is not None or update_data.edges is not None:
            # Build new node/line mapping
            mock_create = CustomGridCreate(
                grid_id=grid_id,
                name=new_name,
                description=new_desc,
                nodes=update_data.nodes if update_data.nodes is not None else [
                    n for n in self._electricity_grid_to_pydantic(existing_grid).nodes
                ],
                edges=update_data.edges if update_data.edges is not None else [
                    e for e in self._electricity_grid_to_pydantic(existing_grid).edges
                ],
                metadata=new_meta,
            )
            new_eg = self._pydantic_to_electricity_grid(mock_create, grid_id=grid_id)
        else:
            new_eg = existing_grid
            new_eg.name = new_name
            new_eg.description = new_desc
            new_eg.metadata = new_meta

        validation_errors = new_eg.validate_grid()
        if validation_errors:
            raise ValueError(f"Topological validation failed: {'; '.join(validation_errors)}")

        now_iso = datetime.now(timezone.utc).isoformat()
        self._custom_grids[grid_id] = new_eg
        if grid_id in self._custom_grid_metadata:
            self._custom_grid_metadata[grid_id]["updated_at"] = now_iso
        else:
            self._custom_grid_metadata[grid_id] = {"created_at": now_iso, "updated_at": now_iso}

        return self._electricity_grid_to_pydantic(
            new_eg,
            is_active=(self._active_grid_id == grid_id),
            is_reference=False,
        )

    def delete_custom_grid(self, grid_id: str) -> bool:
        """Deletes a custom grid from the in-memory registry."""
        if grid_id == self._reference_grid_id or grid_id == "pulseiq-digital-twin":
            raise ValueError("Reference demonstration grid cannot be deleted.")

        if grid_id not in self._custom_grids:
            return False

        if self._active_grid_id == grid_id:
            self._active_grid_id = self._reference_grid_id

        del self._custom_grids[grid_id]
        if grid_id in self._custom_grid_metadata:
            del self._custom_grid_metadata[grid_id]

        return True

    def _pydantic_to_electricity_grid(
        self,
        grid_data: Union[CustomGridCreate, CustomGridUpdate],
        grid_id: str,
    ) -> ElectricityGrid:
        """Converts CustomGridCreate payload into an ai.models.grid.ElectricityGrid instance."""
        ai_nodes: Dict[str, AIGridNode] = {}
        ai_lines: Dict[str, AITransmissionLine] = {}

        type_map = {
            NodeType.CONVENTIONAL_GENERATOR: AINodeType.GENERATOR,
            NodeType.SOLAR_PLANT: AINodeType.SOLAR,
            NodeType.WIND_PLANT: AINodeType.WIND,
            NodeType.BATTERY: AINodeType.BATTERY,
            NodeType.SUBSTATION: AINodeType.SUBSTATION,
            NodeType.LOAD: AINodeType.LOAD_NORMAL,
            NodeType.CRITICAL_LOAD: AINodeType.LOAD_CRITICAL,
        }

        status_map = {
            NodeStatus.ONLINE: AIComponentStatus.ONLINE,
            NodeStatus.OFFLINE: AIComponentStatus.OFFLINE,
            NodeStatus.DEGRADED: AIComponentStatus.DEGRADED,
            NodeStatus.CONGESTED: AIComponentStatus.ONLINE,
        }

        crit_map = {
            NodeCriticality.LOW: AICriticalityLevel.LOW,
            NodeCriticality.MEDIUM: AICriticalityLevel.MEDIUM,
            NodeCriticality.HIGH: AICriticalityLevel.HIGH,
            NodeCriticality.CRITICAL: AICriticalityLevel.CRITICAL,
        }

        for n in grid_data.nodes or []:
            ai_type = type_map.get(n.type, AINodeType.LOAD_NORMAL)
            ai_status = status_map.get(n.status, AIComponentStatus.ONLINE)
            ai_crit = crit_map.get(n.criticality, AICriticalityLevel.MEDIUM)

            gen_mw = 0.0
            dem_mw = 0.0
            ren_mw = 0.0

            if ai_type in (AINodeType.GENERATOR, AINodeType.SOLAR, AINodeType.WIND):
                gen_mw = n.current_output_mw
                if ai_type in (AINodeType.SOLAR, AINodeType.WIND):
                    ren_mw = n.current_output_mw
            elif ai_type == AINodeType.BATTERY:
                gen_mw = max(0.0, n.current_output_mw)
            elif ai_type in (AINodeType.LOAD_NORMAL, AINodeType.LOAD_CRITICAL):
                dem_mw = n.current_output_mw

            meta = dict(n.metadata or {})
            if n.position:
                meta["position"] = {"x": n.position.x, "y": n.position.y}

            ai_nodes[n.id] = AIGridNode(
                id=n.id,
                name=n.name,
                node_type=ai_type,
                status=ai_status,
                operational=AIOperationalData(
                    generation_mw=gen_mw,
                    demand_mw=dem_mw,
                    renewable_generation_mw=ren_mw,
                    max_capacity_mw=n.capacity_mw,
                    min_capacity_mw=0.0,
                    voltage_kv=float(meta.get("voltage_kv", 115.0)),
                    voltage_pu=1.0,
                    frequency_hz=60.0,
                    battery_soc_pct=float(meta.get("state_of_charge_percent", 75.0)) if ai_type == AINodeType.BATTERY else 0.0,
                    battery_capacity_mwh=float(meta.get("capacity_mwh", n.capacity_mw * 2.0)) if ai_type == AINodeType.BATTERY else 0.0,
                    battery_max_power_mw=n.capacity_mw if ai_type == AINodeType.BATTERY else 0.0,
                ),
                risk=AIRiskMetrics(
                    criticality=ai_crit,
                    failure_probability=min(1.0, max(0.0, n.risk_score * 0.05)),
                    risk_score=n.risk_score * 100.0 if n.risk_score <= 1.0 else n.risk_score,
                ),
                location={"lat": n.latitude, "lon": n.longitude} if n.latitude is not None and n.longitude is not None else None,
                metadata=meta,
            )

        for e in grid_data.edges or []:
            e_status = AIComponentStatus.TRIPPED if e.status == EdgeStatus.TRIPPED else AIComponentStatus.ONLINE
            ai_lines[e.id] = AITransmissionLine(
                id=e.id,
                name=e.id,
                source_node_id=e.source,
                target_node_id=e.target,
                capacity_mw=e.capacity_mw,
                current_flow_mw=e.power_flow_mw,
                resistance_ohm=e.resistance_ohms if e.resistance_ohms is not None else 0.02,
                reactance_ohm=e.reactance_ohms if e.reactance_ohms is not None else 0.08,
                status=e_status,
                risk=AIRiskMetrics(
                    criticality=AICriticalityLevel.HIGH if e.capacity_mw >= 400.0 else AICriticalityLevel.MEDIUM,
                    failure_probability=min(1.0, max(0.0, e.risk_score * 0.05)),
                    risk_score=e.risk_score * 100.0 if e.risk_score <= 1.0 else e.risk_score,
                ),
                metadata=dict(e.metadata or {}),
            )

        return ElectricityGrid(
            grid_id=grid_id,
            name=grid_data.name or "Custom Electricity Grid",
            description=grid_data.description or "",
            nodes=ai_nodes,
            lines=ai_lines,
            metadata=dict(getattr(grid_data, "metadata", {}) or {}),
        )

    def _electricity_grid_to_pydantic(
        self,
        eg: ElectricityGrid,
        is_active: bool = False,
        is_reference: bool = False,
    ) -> GridDetailResponse:
        """Converts an ElectricityGrid instance into a GridDetailResponse."""
        nodes: List[GridNode] = []
        edges: List[GridEdge] = []

        type_map = {
            AINodeType.GENERATOR: NodeType.CONVENTIONAL_GENERATOR,
            AINodeType.SOLAR: NodeType.SOLAR_PLANT,
            AINodeType.WIND: NodeType.WIND_PLANT,
            AINodeType.BATTERY: NodeType.BATTERY,
            AINodeType.SUBSTATION: NodeType.SUBSTATION,
            AINodeType.LOAD_NORMAL: NodeType.LOAD,
            AINodeType.LOAD_CRITICAL: NodeType.CRITICAL_LOAD,
        }

        status_map = {
            AIComponentStatus.ONLINE: NodeStatus.ONLINE,
            AIComponentStatus.OFFLINE: NodeStatus.OFFLINE,
            AIComponentStatus.DEGRADED: NodeStatus.DEGRADED,
            AIComponentStatus.TRIPPED: NodeStatus.OFFLINE,
            AIComponentStatus.MAINTENANCE: NodeStatus.DEGRADED,
        }

        crit_map = {
            AICriticalityLevel.LOW: NodeCriticality.LOW,
            AICriticalityLevel.MEDIUM: NodeCriticality.MEDIUM,
            AICriticalityLevel.HIGH: NodeCriticality.HIGH,
            AICriticalityLevel.CRITICAL: NodeCriticality.CRITICAL,
        }

        for n in eg.nodes.values():
            pos_dict = n.metadata.get("position") if isinstance(n.metadata, dict) else None
            pos = (
                GridNodePosition(x=float(pos_dict["x"]), y=float(pos_dict["y"]))
                if isinstance(pos_dict, dict) and "x" in pos_dict and "y" in pos_dict
                else None
            )

            cap = n.operational.max_capacity_mw
            output = (
                n.operational.generation_mw
                if n.node_type in (AINodeType.GENERATOR, AINodeType.SOLAR, AINodeType.WIND, AINodeType.BATTERY)
                else n.operational.demand_mw
            )
            util_pct = (output / cap * 100.0) if cap > 0 else 0.0

            nodes.append(
                GridNode(
                    id=n.id,
                    name=n.name,
                    type=type_map.get(n.node_type, NodeType.LOAD),
                    capacity_mw=cap,
                    current_output_mw=output,
                    status=status_map.get(n.status, NodeStatus.ONLINE),
                    criticality=crit_map.get(n.risk.criticality, NodeCriticality.MEDIUM),
                    utilization_percent=round(util_pct, 2),
                    risk_score=round(n.risk.risk_score / 100.0 if n.risk.risk_score > 1.0 else n.risk.risk_score, 4),
                    latitude=n.location.get("lat") if n.location else None,
                    longitude=n.location.get("lon") if n.location else None,
                    position=pos,
                    metadata=dict(n.metadata or {}),
                )
            )

        for l in eg.lines.values():
            e_status = EdgeStatus.TRIPPED if l.status == AIComponentStatus.TRIPPED else EdgeStatus.NORMAL
            edges.append(
                GridEdge(
                    id=l.id,
                    source=l.source_node_id,
                    target=l.target_node_id,
                    capacity_mw=l.capacity_mw,
                    power_flow_mw=l.current_flow_mw,
                    utilization_percent=round(l.utilization_pct, 2),
                    status=e_status,
                    risk_score=round(l.risk.risk_score / 100.0 if l.risk.risk_score > 1.0 else l.risk.risk_score, 4),
                    resistance_ohms=l.resistance_ohm,
                    reactance_ohms=l.reactance_ohm,
                    metadata=dict(l.metadata or {}),
                )
            )

        tot_gen = eg.total_generation_mw
        tot_dem = eg.total_demand_mw
        ren_pct = (eg.total_renewable_generation_mw / tot_gen * 100.0) if tot_gen > 0 else 0.0
        bat_node = next((n for n in eg.nodes.values() if n.node_type == AINodeType.BATTERY), None)
        bat_soc = bat_node.operational.battery_soc_pct if bat_node else 0.0

        summary = GridSummary(
            total_generation_mw=round(tot_gen, 2),
            total_demand_mw=round(tot_dem, 2),
            renewable_percentage=round(ren_pct, 2),
            battery_soc=round(bat_soc, 2),
            grid_risk_index=0.10,
            active_contingencies_count=sum(1 for l in eg.lines.values() if l.status != AIComponentStatus.ONLINE),
            net_power_balance_mw=round(tot_gen - tot_dem, 2),
        )

        val_errors = eg.validate_grid()

        return GridDetailResponse(
            grid_id=eg.grid_id,
            name=eg.name,
            description=eg.description,
            is_reference=is_reference,
            is_active=is_active,
            nodes=nodes,
            edges=edges,
            summary=summary,
            validation_errors=val_errors,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def get_all_component_ids(self) -> Set[str]:
        """Returns the set of all valid node and edge identifiers for active grid."""
        active_eg = self.get_active_grid()
        node_ids = set(active_eg.nodes.keys())
        edge_ids = set(active_eg.lines.keys())
        return node_ids.union(edge_ids)

    def component_exists(self, component_id: str) -> bool:
        """Validates whether a component exists in the active grid topology."""
        return component_id in self.get_all_component_ids()

    def get_node_by_id(self, node_id: str) -> Optional[GridNode]:
        """Retrieves a specific node by ID from active grid state."""
        state = self.get_grid_state()
        for node in state.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edge_by_id(self, edge_id: str) -> Optional[GridEdge]:
        """Retrieves a specific transmission edge by ID from active grid state."""
        state = self.get_grid_state()
        for edge in state.edges:
            if edge.id == edge_id:
                return edge
        return None


grid_service = GridService()

