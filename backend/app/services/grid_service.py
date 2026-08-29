from datetime import datetime, timezone
from typing import List, Optional, Set
from backend.app.schemas.grid import (
    NodeType,
    NodeStatus,
    NodeCriticality,
    EdgeStatus,
    GridNodePosition,
    GridNode,
    GridEdge,
    GridSummary,
    GridResponse,
)


class GridService:
    """Service providing realistic electricity grid topology, asset states, and telemetry.
    Features an expansive 50-node enterprise digital twin network with 80+ interconnected
    multi-path transmission branches, meshed 400kV rings, BESS buffers, and dual-fed critical loads.
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

    def get_grid_state(self) -> GridResponse:
        """Calculates and returns the complete current grid state with summary metrics."""
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
            nodes=self._nodes,
            edges=self._edges,
            summary=summary,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def get_all_component_ids(self) -> Set[str]:
        """Returns the set of all valid node and edge identifiers."""
        node_ids = {node.id for node in self._nodes}
        edge_ids = {edge.id for edge in self._edges}
        return node_ids.union(edge_ids)

    def component_exists(self, component_id: str) -> bool:
        """Validates whether a component exists in the grid topology."""
        return component_id in self.get_all_component_ids()

    def get_node_by_id(self, node_id: str) -> Optional[GridNode]:
        """Retrieves a specific node by ID."""
        for node in self._nodes:
            if node.id == node_id:
                return node
        return None

    def get_edge_by_id(self, edge_id: str) -> Optional[GridEdge]:
        """Retrieves a specific transmission edge by ID."""
        for edge in self._edges:
            if edge.id == edge_id:
                return edge
        return None


grid_service = GridService()
