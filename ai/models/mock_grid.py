"""
PULSEiQ - Initial Demonstration Mock Grid
Realistic electricity grid topology with generators, renewable solar/wind assets,
battery energy storage system (BESS), transmission/distribution substations,
and critical & normal consumer loads.
"""

from ai.models.grid import (
    ComponentStatus,
    CriticalityLevel,
    ElectricityGrid,
    GridNode,
    NodeType,
    OperationalData,
    RiskMetrics,
    TransmissionLine,
)


def create_mock_grid(grid_id: str = "pulseiq_demo_grid_01") -> ElectricityGrid:
    """
    Constructs a realistic regional demonstration grid with 12 nodes and 12 lines.
    Topology:
      - Generator (Gas CCGT 120MW) -> Main Substation (230kV/69kV)
      - Solar Farm (45MW) -> Main Substation
      - Wind Farm (50MW) -> Main Substation
      - BESS Storage (15MW / 40MWh) -> Main Substation
      - Main Substation -> North Distribution Substation (69kV/13.8kV)
      - Main Substation -> South Distribution Substation (69kV/13.8kV)
      - North Substation -> Regional General Hospital [CRITICAL LOAD] (8.5MW)
      - North Substation -> North Residential Community [NORMAL LOAD] (35.0MW)
      - South Substation -> Metro High-Reliability Data Center [CRITICAL LOAD] (18.0MW)
      - South Substation -> South Industrial & Manufacturing Park [NORMAL LOAD] (42.0MW)
      - Main Substation -> Downtown Commercial & Financial Hub [NORMAL LOAD] (25.0MW)
      - North Substation <-> South Substation Tie-Line (Redundant contingency line)
    """
    grid = ElectricityGrid(
        grid_id=grid_id,
        name="PULSEiQ Regional Demonstration Grid",
        description="A regional 230kV/69kV/13.8kV test network featuring mixed generation, renewable sources, storage, and critical loads.",
        metadata={
            "region": "Midwest Interconnection",
            "base_mva": 100.0,
            "nominal_frequency_hz": 60.0,
            "created_for": "PULSEiQ AI/ML, Simulation & Optimization Platform",
        },
    )

    # --------------------------------------------------------------------------
    # 1. NODES / COMPONENTS
    # --------------------------------------------------------------------------

    # --- Generation Assets ---
    # Thermal Natural Gas Combined Cycle Plant (Base Load)
    grid.add_node(
        GridNode(
            id="gen_gas_01",
            name="Apex Natural Gas Combined Cycle Plant",
            node_type=NodeType.GENERATOR,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=75.0,
                demand_mw=0.0,
                max_capacity_mw=120.0,
                min_capacity_mw=25.0,
                voltage_kv=230.0,
                voltage_pu=1.02,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.015,
                risk_score=15.0,
                vulnerability_factor=1.1,
                historical_failures_count=2,
            ),
            location={"lat": 41.8781, "lon": -87.6298},
            tags=["generation", "conventional", "gas_ccgt", "base_load"],
            metadata={"fuel_type": "natural_gas", "ramp_rate_mw_per_min": 8.0, "heat_rate_btu_kwh": 6800},
        )
    )

    # Solaria Solar PV Farm (Renewable)
    grid.add_node(
        GridNode(
            id="solar_farm_01",
            name="Solaria 45MW Solar PV Farm",
            node_type=NodeType.SOLAR,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=32.0,
                renewable_generation_mw=32.0,
                demand_mw=0.0,
                max_capacity_mw=45.0,
                min_capacity_mw=0.0,
                voltage_kv=69.0,
                voltage_pu=1.01,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.025,
                risk_score=12.0,
                vulnerability_factor=1.4,  # Weather-dependent
                historical_failures_count=1,
            ),
            location={"lat": 41.9200, "lon": -87.5800},
            tags=["generation", "renewable", "solar_pv", "clean_energy"],
            metadata={"inverter_efficiency": 0.98, "irradiance_w_m2": 820.0},
        )
    )

    # Coastal Breeze Wind Farm (Renewable)
    grid.add_node(
        GridNode(
            id="wind_farm_01",
            name="Coastal Breeze 50MW Wind Turbine Array",
            node_type=NodeType.WIND,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=28.0,
                renewable_generation_mw=28.0,
                demand_mw=0.0,
                max_capacity_mw=50.0,
                min_capacity_mw=0.0,
                voltage_kv=69.0,
                voltage_pu=1.00,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.035,
                risk_score=18.0,
                vulnerability_factor=1.6,  # Gusts / mechanical wear
                historical_failures_count=3,
            ),
            location={"lat": 42.0100, "lon": -87.5200},
            tags=["generation", "renewable", "wind_turbine", "clean_energy"],
            metadata={"cut_in_speed_mps": 3.0, "rated_speed_mps": 12.0, "cut_out_speed_mps": 25.0},
        )
    )

    # Battery Energy Storage System (BESS)
    grid.add_node(
        GridNode(
            id="bess_storage_01",
            name="Metro Grid-Scale BESS (15MW / 40MWh)",
            node_type=NodeType.BATTERY,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,  # Standby / floating mode
                demand_mw=0.0,
                max_capacity_mw=15.0,
                min_capacity_mw=-15.0,  # Charging capability
                voltage_kv=69.0,
                voltage_pu=1.00,
                frequency_hz=60.0,
                battery_soc_pct=78.5,
                battery_capacity_mwh=40.0,
                battery_max_power_mw=15.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.010,
                risk_score=10.0,
                vulnerability_factor=1.0,
                historical_failures_count=0,
            ),
            location={"lat": 41.8500, "lon": -87.6500},
            tags=["storage", "bess", "fast_response", "ancillary_services"],
            metadata={"chemistry": "Lithium Iron Phosphate (LFP)", "round_trip_efficiency": 0.89},
        )
    )

    # --- Substations ---
    # Main Bulk Transmission Substation
    grid.add_node(
        GridNode(
            id="sub_trans_main",
            name="Central Bulk Transmission Substation (230kV/69kV)",
            node_type=NodeType.SUBSTATION,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=0.0,
                voltage_kv=230.0,
                voltage_pu=1.02,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.CRITICAL,
                failure_probability=0.005,
                risk_score=25.0,
                vulnerability_factor=1.0,
                historical_failures_count=0,
            ),
            location={"lat": 41.8700, "lon": -87.6300},
            tags=["substation", "transmission", "bulk_grid", "backbone"],
            metadata={"transformer_count": 3, "transformer_mva_rating": 150.0},
        )
    )

    # North Distribution Substation
    grid.add_node(
        GridNode(
            id="sub_dist_north",
            name="North District Distribution Substation (69kV/13.8kV)",
            node_type=NodeType.SUBSTATION,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=0.0,
                voltage_kv=69.0,
                voltage_pu=0.99,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.012,
                risk_score=14.0,
                vulnerability_factor=1.1,
                historical_failures_count=1,
            ),
            location={"lat": 41.9400, "lon": -87.6600},
            tags=["substation", "distribution", "north_sector"],
            metadata={"feeder_count": 6},
        )
    )

    # South Distribution Substation
    grid.add_node(
        GridNode(
            id="sub_dist_south",
            name="South District Distribution Substation (69kV/13.8kV)",
            node_type=NodeType.SUBSTATION,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=0.0,
                voltage_kv=69.0,
                voltage_pu=0.99,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.012,
                risk_score=14.0,
                vulnerability_factor=1.1,
                historical_failures_count=1,
            ),
            location={"lat": 41.8000, "lon": -87.6400},
            tags=["substation", "distribution", "south_sector"],
            metadata={"feeder_count": 8},
        )
    )

    # --- Critical Loads ---
    # Regional Trauma Hospital
    grid.add_node(
        GridNode(
            id="load_hospital_main",
            name="St. Jude Regional Trauma Center & Hospital",
            node_type=NodeType.LOAD_CRITICAL,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=8.5,
                max_capacity_mw=12.0,
                voltage_kv=13.8,
                voltage_pu=0.99,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.CRITICAL,
                failure_probability=0.001,
                risk_score=30.0,
                vulnerability_factor=1.8,
                historical_failures_count=0,
            ),
            location={"lat": 41.9500, "lon": -87.6700},
            tags=["load", "critical", "healthcare", "life_safety"],
            metadata={"backup_generators": 2, "backup_fuel_hours": 72, "priority_tier": 1},
        )
    )

    # Metro Data Center
    grid.add_node(
        GridNode(
            id="load_datacenter_01",
            name="Metro Tier-IV Cloud Data Center",
            node_type=NodeType.LOAD_CRITICAL,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=18.0,
                max_capacity_mw=22.0,
                voltage_kv=13.8,
                voltage_pu=0.99,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.CRITICAL,
                failure_probability=0.004,
                risk_score=22.0,
                vulnerability_factor=1.4,
                historical_failures_count=0,
            ),
            location={"lat": 41.7900, "lon": -87.6100},
            tags=["load", "critical", "datacenter", "digital_infrastructure"],
            metadata={"tier_rating": "Tier IV", "sla_availability_pct": 99.995},
        )
    )

    # --- Normal Loads ---
    # North Residential District
    grid.add_node(
        GridNode(
            id="load_residential_north",
            name="North Suburban Residential Community (45,000 households)",
            node_type=NodeType.LOAD_NORMAL,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=35.0,
                max_capacity_mw=45.0,
                voltage_kv=13.8,
                voltage_pu=0.98,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.020,
                risk_score=8.0,
                vulnerability_factor=1.0,
                historical_failures_count=3,
            ),
            location={"lat": 41.9700, "lon": -87.6800},
            tags=["load", "normal", "residential", "community"],
            metadata={"customer_count": 45000, "smart_meter_coverage_pct": 94.0},
        )
    )

    # South Industrial & Manufacturing Park
    grid.add_node(
        GridNode(
            id="load_industrial_south",
            name="South Heavy Industrial & Advanced Manufacturing Park",
            node_type=NodeType.LOAD_NORMAL,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=42.0,
                max_capacity_mw=55.0,
                voltage_kv=13.8,
                voltage_pu=0.98,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.022,
                risk_score=9.0,
                vulnerability_factor=1.1,
                historical_failures_count=2,
            ),
            location={"lat": 41.7700, "lon": -87.6700},
            tags=["load", "normal", "industrial", "high_demand"],
            metadata={"heavy_motor_loads_pct": 65.0, "power_factor": 0.88},
        )
    )

    # Downtown Commercial Hub
    grid.add_node(
        GridNode(
            id="load_commercial_central",
            name="Downtown Commercial Financial Hub & Retail Centers",
            node_type=NodeType.LOAD_NORMAL,
            status=ComponentStatus.ONLINE,
            operational=OperationalData(
                generation_mw=0.0,
                demand_mw=25.0,
                max_capacity_mw=35.0,
                voltage_kv=13.8,
                voltage_pu=0.99,
                frequency_hz=60.0,
            ),
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.018,
                risk_score=7.5,
                vulnerability_factor=1.0,
                historical_failures_count=1,
            ),
            location={"lat": 41.8850, "lon": -87.6250},
            tags=["load", "normal", "commercial", "urban"],
            metadata={"hvac_load_pct": 45.0, "commercial_tenants": 320},
        )
    )

    # --------------------------------------------------------------------------
    # 2. TRANSMISSION & DISTRIBUTION LINES
    # --------------------------------------------------------------------------

    # Line: Gas Plant -> Central Transmission Substation (230kV)
    grid.add_line(
        TransmissionLine(
            id="line_gen_to_submain",
            name="230kV Gas Plant Bulk Infeed",
            source_node_id="gen_gas_01",
            target_node_id="sub_trans_main",
            capacity_mw=150.0,
            current_flow_mw=75.0,
            resistance_ohm=0.012,
            reactance_ohm=0.045,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=230.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.008,
                risk_score=16.0,
            ),
            tags=["transmission", "bulk_infeed", "230kv"],
        )
    )

    # Line: Solar Farm -> Central Transmission Substation (69kV)
    grid.add_line(
        TransmissionLine(
            id="line_solar_to_submain",
            name="69kV Solaria PV Collector Feeder",
            source_node_id="solar_farm_01",
            target_node_id="sub_trans_main",
            capacity_mw=60.0,
            current_flow_mw=32.0,
            resistance_ohm=0.035,
            reactance_ohm=0.082,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.015,
                risk_score=9.0,
            ),
            tags=["transmission", "renewable_collector", "69kv"],
        )
    )

    # Line: Wind Farm -> Central Transmission Substation (69kV)
    grid.add_line(
        TransmissionLine(
            id="line_wind_to_submain",
            name="69kV Coastal Wind Interconnection",
            source_node_id="wind_farm_01",
            target_node_id="sub_trans_main",
            capacity_mw=60.0,
            current_flow_mw=28.0,
            resistance_ohm=0.040,
            reactance_ohm=0.095,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.018,
                risk_score=11.0,
            ),
            tags=["transmission", "renewable_collector", "69kv"],
        )
    )

    # Line: BESS Storage -> Central Transmission Substation (69kV)
    grid.add_line(
        TransmissionLine(
            id="line_bess_to_submain",
            name="69kV BESS Storage Bi-directional Tie",
            source_node_id="bess_storage_01",
            target_node_id="sub_trans_main",
            capacity_mw=25.0,
            current_flow_mw=0.0,  # floating
            resistance_ohm=0.020,
            reactance_ohm=0.050,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.009,
                risk_score=10.0,
            ),
            tags=["transmission", "storage_tie", "bidirectional"],
        )
    )

    # Line: Central Transmission Substation -> North Distribution Substation (69kV)
    grid.add_line(
        TransmissionLine(
            id="line_submain_to_subnorth",
            name="69kV North District Primary Sub-transmission Trunk",
            source_node_id="sub_trans_main",
            target_node_id="sub_dist_north",
            capacity_mw=80.0,
            current_flow_mw=43.5,
            resistance_ohm=0.028,
            reactance_ohm=0.072,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.011,
                risk_score=15.0,
            ),
            tags=["transmission", "trunk", "69kv"],
        )
    )

    # Line: Central Transmission Substation -> South Distribution Substation (69kV)
    grid.add_line(
        TransmissionLine(
            id="line_submain_to_subsouth",
            name="69kV South District Primary Sub-transmission Trunk",
            source_node_id="sub_trans_main",
            target_node_id="sub_dist_south",
            capacity_mw=90.0,
            current_flow_mw=60.0,
            resistance_ohm=0.025,
            reactance_ohm=0.068,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.012,
                risk_score=16.0,
            ),
            tags=["transmission", "trunk", "69kv"],
        )
    )

    # Line: Central Transmission Substation -> Downtown Commercial Load (13.8kV)
    grid.add_line(
        TransmissionLine(
            id="line_submain_to_commercial",
            name="13.8kV Downtown Commercial Feeder",
            source_node_id="sub_trans_main",
            target_node_id="load_commercial_central",
            capacity_mw=40.0,
            current_flow_mw=25.0,
            resistance_ohm=0.045,
            reactance_ohm=0.088,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=13.8,
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.014,
                risk_score=8.5,
            ),
            tags=["distribution", "commercial_feeder", "13.8kv"],
        )
    )

    # Line: North Distribution Substation -> Hospital (13.8kV Dedicated Critical Feeder)
    grid.add_line(
        TransmissionLine(
            id="line_subnorth_to_hospital",
            name="13.8kV Dedicated Hospital Life-Safety Feeder",
            source_node_id="sub_dist_north",
            target_node_id="load_hospital_main",
            capacity_mw=16.0,
            current_flow_mw=8.5,
            resistance_ohm=0.018,
            reactance_ohm=0.038,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=13.8,
            risk=RiskMetrics(
                criticality=CriticalityLevel.CRITICAL,
                failure_probability=0.003,
                risk_score=28.0,
            ),
            tags=["distribution", "critical_feeder", "hospital", "priority_service"],
        )
    )

    # Line: North Distribution Substation -> Residential Community (13.8kV)
    grid.add_line(
        TransmissionLine(
            id="line_subnorth_to_residential",
            name="13.8kV North Residential Distribution Main",
            source_node_id="sub_dist_north",
            target_node_id="load_residential_north",
            capacity_mw=50.0,
            current_flow_mw=35.0,
            resistance_ohm=0.052,
            reactance_ohm=0.098,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=13.8,
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.018,
                risk_score=9.2,
            ),
            tags=["distribution", "residential_feeder", "13.8kv"],
        )
    )

    # Line: South Distribution Substation -> Data Center (13.8kV Dual-Redundant Feeder)
    grid.add_line(
        TransmissionLine(
            id="line_subsouth_to_datacenter",
            name="13.8kV Dedicated Tier-IV Data Center Feeder",
            source_node_id="sub_dist_south",
            target_node_id="load_datacenter_01",
            capacity_mw=30.0,
            current_flow_mw=18.0,
            resistance_ohm=0.022,
            reactance_ohm=0.042,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=13.8,
            risk=RiskMetrics(
                criticality=CriticalityLevel.CRITICAL,
                failure_probability=0.004,
                risk_score=24.0,
            ),
            tags=["distribution", "critical_feeder", "datacenter"],
        )
    )

    # Line: South Distribution Substation -> Industrial Park (13.8kV Industrial Feeder)
    grid.add_line(
        TransmissionLine(
            id="line_subsouth_to_industrial",
            name="13.8kV South Industrial Feeder",
            source_node_id="sub_dist_south",
            target_node_id="load_industrial_south",
            capacity_mw=60.0,
            current_flow_mw=42.0,
            resistance_ohm=0.038,
            reactance_ohm=0.084,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=13.8,
            risk=RiskMetrics(
                criticality=CriticalityLevel.MEDIUM,
                failure_probability=0.016,
                risk_score=10.5,
            ),
            tags=["distribution", "industrial_feeder", "13.8kv"],
        )
    )

    # Line: North Substation <-> South Substation (69kV Inter-tie contingency line)
    grid.add_line(
        TransmissionLine(
            id="line_tie_north_south",
            name="69kV North-South Emergency Tie Line",
            source_node_id="sub_dist_north",
            target_node_id="sub_dist_south",
            capacity_mw=45.0,
            current_flow_mw=0.0,  # Standby / Normally open tie
            resistance_ohm=0.042,
            reactance_ohm=0.096,
            status=ComponentStatus.ONLINE,
            voltage_level_kv=69.0,
            risk=RiskMetrics(
                criticality=CriticalityLevel.HIGH,
                failure_probability=0.010,
                risk_score=12.0,
            ),
            tags=["transmission", "tie_line", "redundancy", "contingency_support"],
        )
    )

    return grid
