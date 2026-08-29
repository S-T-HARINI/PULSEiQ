// TypeScript definitions corresponding to PULSEiQ Backend FastAPI schemas

export type NodeType =
  | "conventional_generator"
  | "solar_plant"
  | "wind_plant"
  | "battery"
  | "substation"
  | "load"
  | "critical_load";

export type NodeStatus = "online" | "offline" | "degraded" | "congested";
export type NodeCriticality = "low" | "medium" | "high" | "critical";
export type EdgeStatus = "normal" | "congested" | "tripped" | "maintenance";

export interface GridNodePosition {
  x?: number;
  y?: number;
}

export interface GridNodeApi {
  id: string;
  name: string;
  type: NodeType;
  capacity_mw: number;
  current_output_mw: number;
  status: NodeStatus;
  criticality: NodeCriticality;
  utilization_percent: number;
  risk_score: number;
  latitude?: number;
  longitude?: number;
  position?: GridNodePosition;
  metadata?: Record<string, unknown>;
}

export interface GridEdgeApi {
  id: string;
  source: string;
  target: string;
  capacity_mw: number;
  power_flow_mw: number;
  utilization_percent: number;
  status: EdgeStatus;
  risk_score: number;
  resistance_ohms?: number;
  reactance_ohms?: number;
  metadata?: Record<string, unknown>;
}

export interface GridSummaryApi {
  total_generation_mw: number;
  total_demand_mw: number;
  renewable_percentage: number;
  battery_soc: number;
  grid_risk_index: number;
  active_contingencies_count: number;
  net_power_balance_mw: number;
}

export interface GridResponse {
  nodes: GridNodeApi[];
  edges: GridEdgeApi[];
  summary: GridSummaryApi;
  timestamp?: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  ai_modules: {
    forecasting: string;
    simulation: string;
    risk_engine: string;
    optimization: string;
  };
  environment: string;
}

export interface ForecastDataPoint {
  timestamp: string;
  predicted_demand_mw?: number;
  predicted_renewable_mw?: number;
  value_mw: number;
  lower_bound_mw?: number;
  upper_bound_mw?: number;
}

export interface ForecastRequest {
  forecast_type?: "load" | "solar" | "wind";
  horizon_hours?: number;
  historical_demand_mw?: number[];
  weather_info?: Record<string, unknown>;
  renewable_generation_info?: Record<string, unknown>;
  region_id?: string;
}

export interface ForecastResponse {
  forecast_type: "load" | "solar" | "wind";
  horizon_hours: number;
  values: ForecastDataPoint[];
  peak_mw: number;
  min_mw: number;
  average_mw: number;
  confidence_score: number;
  model_source: string;
  generated_at: string;
}

export interface SimulationRunRequest {
  scenario_id?: string;
  duration_hours?: number;
  time_step_minutes?: number;
  demand_mw?: number;
  generation_mw?: number;
  renewable_generation_mw?: number;
  battery_state?: Record<string, unknown>;
  load_growth_factor?: number;
  contingency_event?: string;
  grid_state?: Record<string, unknown>;
  simulation_parameters?: Record<string, unknown>;
}

export interface SimulationRunResponse {
  simulation_status: string;
  total_generation_mw: number;
  total_demand_mw: number;
  renewable_generation_mw: number;
  line_utilization_avg: number;
  line_loading: Record<string, number>;
  frequency_hz: number;
  voltage_indicators: {
    min_voltage_pu: number;
    max_voltage_pu: number;
    avg_voltage_pu: number;
  };
  simulation_warnings: string[];
  affected_components: string[];
  risk_index: number;
  resulting_grid_state?: Record<string, unknown>;
  model_source: string;
  timestamp: string;
  details: Record<string, unknown>;
}

export interface RiskAnalysisRequest {
  contingency_type?: string;
  scenario_info?: string;
  failed_component_id?: string;
  monte_carlo_iterations?: number;
  grid_state?: Record<string, unknown>;
  simulation_results?: Record<string, unknown>;
}

export interface AffectedComponent {
  id: string;
  name: string;
  type: string;
  impact: string;
  utilization_or_loading?: number;
}

export interface CriticalLoadImpact {
  critical_load_at_risk: boolean;
  critical_load_at_risk_mw: number;
  affected_critical_facilities: string[];
}

export interface RiskAnalysisResponse {
  risk_index: number;
  risk_level: "low" | "moderate" | "high" | "critical";
  vulnerable_components: AffectedComponent[];
  affected_components: AffectedComponent[];
  critical_load_impact: CriticalLoadImpact;
  contingency_results: Record<string, unknown>;
  n1_analysis: Record<string, unknown>;
  cascading_failure_indicators: Record<string, unknown>;
  model_source: string;
  explanation: string;
  summary: Record<string, unknown>;
  analyzed_at: string;
}

export interface GeneratorDispatch {
  generator_id: string;
  generator_name: string;
  type: string;
  dispatched_mw: number;
  capacity_mw: number;
  marginal_cost_per_mwh: number;
}

export interface OptimizationRunRequest {
  objective?: "cost_minimization" | "emission_reduction" | "reliability_maximization";
  demand_mw?: number;
  available_generation_mw?: number;
  renewable_generation_mw?: number;
  current_grid_state?: Record<string, unknown>;
  battery_availability?: Record<string, unknown>;
  battery_state?: Record<string, unknown>;
  risk_results?: Record<string, unknown>;
  operational_constraints?: Record<string, unknown>;
  critical_load_requirements?: Record<string, unknown>;
}

export interface OptimizationRunResponse {
  optimization_status: string;
  objective: "cost_minimization" | "emission_reduction" | "reliability_maximization";
  recommended_actions: string[];
  generator_dispatch: GeneratorDispatch[];
  total_dispatched_generation_mw: number;
  battery_dispatch_mw: number;
  battery_charge_discharge_mw: number;
  backup_generation_mw: number;
  flexible_load_reduction_mw: number;
  renewable_curtailment_mw: number;
  unserved_demand_mw: number;
  expected_risk_reduction: number;
  objective_value: number;
  cost_estimate_usd: number;
  model_source: string;
  summary: Record<string, unknown>;
  solved_at: string;
}

export interface ScenarioWhatIfRequest {
  scenario_type: "extreme_heatwave" | "solar_ramp_down" | "n1_line_trip" | "wind_storm_cutoff" | "wind_storm";
  name?: string;
  description?: string;
  demand_multiplier?: number;
  solar_multiplier?: number;
  wind_multiplier?: number;
  battery_available?: boolean;
  failed_component_id?: string;
  current_grid_state?: Record<string, unknown>;
}

export interface ScenarioWhatIfResponse {
  scenario_id: string;
  scenario_type: string;
  scenario_name: string;
  name: string;
  status: string;
  changed_demand_mw: number;
  demand_mw: number;
  changed_generation_mw: number;
  generation_mw: number;
  renewable_share_percent: number;
  resulting_risk_index: number;
  risk_index: number;
  critical_load_reliability_percent: number;
  critical_load_impact: Record<string, unknown>;
  affected_components: string[];
  recommended_response: string[];
  applied_parameters: Record<string, unknown>;
  model_source: string;
  summary: Record<string, unknown>;
  created_at: string;
}

export interface GridTelemetryMessage {
  message_type: string;
  timestamp: string;
  grid_status: "NORMAL" | "WARNING" | "ALERT" | "CRITICAL" | "CONTINGENCY";
  total_generation: number;
  total_demand: number;
  renewable_generation_percent: number;
  battery_soc: number;
  grid_risk_index: number;
  frequency_hz: number;
  line_utilization_avg: number;
  affected_components: string[];
  details: Record<string, unknown>;
}
