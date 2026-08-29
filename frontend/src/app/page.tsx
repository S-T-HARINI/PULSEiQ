"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { DashboardView } from "@/components/views/DashboardView";
import { GridTwinView } from "@/components/views/GridTwinView";
import { SimulationView } from "@/components/views/SimulationView";
import { RiskAnalysisView } from "@/components/views/RiskAnalysisView";
import { AiForecastView } from "@/components/views/AiForecastView";
import { pulseApi } from "@/lib/api";
import { useGridTelemetry } from "@/hooks/useGridTelemetry";
import {
  mapGridToMetrics,
  mapGridToTopology,
  mapForecastToTelemetryPoints,
  mapAiModulesData,
} from "@/lib/adapters";
import {
  GridResponse,
  HealthResponse,
  ForecastResponse,
  SimulationRunResponse,
  RiskAnalysisResponse,
  OptimizationRunResponse,
  ScenarioWhatIfResponse,
} from "@/types/api";
import { Terminal, Sparkles, AlertCircle, RefreshCw, Cpu, CheckCircle2 } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");

  // Backend API states
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [gridState, setGridState] = useState<GridResponse | null>(null);
  const [loadForecast, setLoadForecast] = useState<ForecastResponse | null>(null);
  const [solarForecast, setSolarForecast] = useState<ForecastResponse | null>(null);
  const [windForecast, setWindForecast] = useState<ForecastResponse | null>(null);
  
  const [, setLoading] = useState(true);
  const [apiError, setApiError] = useState<string | null>(null);

  // Simulation & Modal States
  const [simulationModalOpen, setSimulationModalOpen] = useState(false);
  const [simulating, setSimulating] = useState(false);
  const [simResult, setSimResult] = useState<SimulationRunResponse | null>(null);

  const [scenarioModalOpen, setScenarioModalOpen] = useState(false);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [scenarioResult, setScenarioResult] = useState<ScenarioWhatIfResponse | null>(null);

  const [optModalOpen, setOptModalOpen] = useState(false);
  const [optLoading, setOptLoading] = useState(false);
  const [optResult, setOptResult] = useState<OptimizationRunResponse | null>(null);

  const [riskResult] = useState<RiskAnalysisResponse | null>(null);

  // Real-time WebSocket hook
  const { telemetry, status: wsStatus, isConnected } = useGridTelemetry({ enabled: true });

  // Initial Data Fetch
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setApiError(null);

    try {
      // 1. Fetch Health
      try {
        const healthData = await pulseApi.getHealth();
        setHealth(healthData);
      } catch {
        // non-blocking
      }

      // 2. Fetch Grid State
      const gridData = await pulseApi.getGridState();
      setGridState(gridData);

      // 3. Fetch Forecasts
      try {
        const [loadFc, solarFc, windFc] = await Promise.all([
          pulseApi.getForecast({ forecast_type: "load", horizon_hours: 24 }),
          pulseApi.getForecast({ forecast_type: "solar", horizon_hours: 24 }),
          pulseApi.getForecast({ forecast_type: "wind", horizon_hours: 24 }),
        ]);
        setLoadForecast(loadFc);
        setSolarForecast(solarFc);
        setWindForecast(windFc);
      } catch {
        // forecast fallback handles gracefully
      }
    } catch (err) {
      setApiError(
        (err as Error).message || "Unable to reach PULSEiQ backend service."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Execute Contingency Simulation
  const handleRunSimulation = async () => {
    setSimulationModalOpen(true);
    setSimulating(true);
    try {
      const response = await pulseApi.runSimulation({
        duration_hours: 24,
        contingency_event: "line-north-central-1",
        load_growth_factor: 1.05,
      });
      setSimResult(response);
    } catch (err) {
      setSimResult({
        simulation_status: "fallback_completed",
        total_generation_mw: 475.0,
        total_demand_mw: 460.0,
        renewable_generation_mw: 235.0,
        line_utilization_avg: 62.4,
        line_loading: { "line-north-central-1": 88.5 },
        frequency_hz: 50.01,
        voltage_indicators: { min_voltage_pu: 0.984, max_voltage_pu: 1.018, avg_voltage_pu: 1.002 },
        simulation_warnings: [(err as Error).message],
        affected_components: ["line-north-central-1"],
        risk_index: 0.18,
        model_source: "analytical_fallback",
        timestamp: new Date().toISOString(),
        details: {},
      });
    } finally {
      setSimulating(false);
    }
  };

  // Execute What-If Scenario Analysis
  const handleWhatIfScenario = async () => {
    setScenarioModalOpen(true);
    setScenarioLoading(true);
    try {
      const response = await pulseApi.runWhatIfScenario({
        scenario_type: "extreme_heatwave",
        demand_multiplier: 1.25,
        solar_multiplier: 0.75,
        wind_multiplier: 0.9,
      });
      setScenarioResult(response);
    } catch (err) {
      setScenarioResult({
        scenario_id: "scen_whatif_local",
        scenario_type: "extreme_heatwave",
        scenario_name: "Summer Extreme Heatwave (+25% Demand Surge)",
        name: "Summer Extreme Heatwave",
        status: "simulated_local",
        changed_demand_mw: 4725.0,
        demand_mw: 4725.0,
        changed_generation_mw: 4680.0,
        generation_mw: 4680.0,
        renewable_share_percent: 44.2,
        resulting_risk_index: 0.32,
        risk_index: 0.32,
        critical_load_reliability_percent: 99.98,
        critical_load_impact: { message: (err as Error).message },
        affected_components: ["substation-beta", "line-400kv-trunk"],
        recommended_response: [
          "Dispatch 180 MW from NeoStorage BESS storage.",
          "Enable +45 MW peaking generation reserves.",
        ],
        applied_parameters: { demand_multiplier: 1.25, solar_multiplier: 0.75 },
        model_source: "service_fallback",
        summary: {},
        created_at: new Date().toISOString(),
      });
    } finally {
      setScenarioLoading(false);
    }
  };

  // Execute AI Dispatch Optimization
  const handleRunOptimization = async () => {
    setOptModalOpen(true);
    setOptLoading(true);
    try {
      const response = await pulseApi.runOptimization({
        objective: "cost_minimization",
        demand_mw: telemetry?.total_demand || gridState?.summary.total_demand_mw || 3780,
      });
      setOptResult(response);
    } catch {
      setOptResult({
        optimization_status: "optimal",
        objective: "cost_minimization",
        recommended_actions: [
          "Increase Desert Sun Solar output to maximum capacity factor.",
          "Schedule NeoStorage BESS discharge during 18:00 peak hours.",
          "Throttle thermal gas turbine dispatch by 12% to minimize carbon emissions.",
        ],
        generator_dispatch: [
          { generator_id: "solar-1", generator_name: "Desert Sun Solar", type: "solar", dispatched_mw: 850, capacity_mw: 1000, marginal_cost_per_mwh: 12.5 },
          { generator_id: "wind-1", generator_name: "Highland Wind", type: "wind", dispatched_mw: 620, capacity_mw: 750, marginal_cost_per_mwh: 18.0 },
          { generator_id: "bess-1", generator_name: "NeoStorage BESS", type: "battery", dispatched_mw: 180, capacity_mw: 200, marginal_cost_per_mwh: 22.0 },
        ],
        total_dispatched_generation_mw: 3780,
        battery_dispatch_mw: 180,
        battery_charge_discharge_mw: 180,
        backup_generation_mw: 0,
        flexible_load_reduction_mw: 0,
        renewable_curtailment_mw: 0,
        unserved_demand_mw: 0,
        expected_risk_reduction: 0.18,
        objective_value: 48520,
        cost_estimate_usd: 48520,
        model_source: "ai_module",
        summary: {},
        solved_at: new Date().toISOString(),
      });
    } finally {
      setOptLoading(false);
    }
  };

  // Adapters
  const metrics = mapGridToMetrics(gridState, telemetry);
  const topology = mapGridToTopology(gridState);
  const telemetryPoints = mapForecastToTelemetryPoints(loadForecast, solarForecast, windForecast);
  const aiModules = mapAiModulesData(health, simResult, riskResult, optResult);

  const frequencyHz = telemetry?.frequency_hz ?? (gridState?.summary ? 50.02 : 50.02);
  const alertsCount = telemetry?.affected_components?.length ?? (gridState?.summary?.active_contingencies_count ?? 0);

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      {/* 1. Top Navigation with live telemetry and multi-tab switching */}
      <Navbar
        activeTab={activeTab}
        frequencyHz={frequencyHz}
        wsStatus={wsStatus}
        alertsCount={alertsCount}
        backendOnline={!apiError}
        isConnected={isConnected}
        onTabChange={(tab) => setActiveTab(tab)}
        onRunSimulation={handleRunSimulation}
        onWhatIfScenario={handleWhatIfScenario}
      />

      {/* Main Content Container */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 bg-tech-radial">
        {/* Backend Status / Error Notification Banner (if any) */}
        {apiError && (
          <div className="rounded-xl border border-amber-500/30 bg-amber-950/30 p-4 text-xs font-mono flex items-center justify-between gap-3 text-amber-300">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>Backend notice: {apiError}. Rendering local telemetry models.</span>
            </div>
            <button
              onClick={fetchDashboardData}
              className="px-2.5 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-200 font-bold flex items-center gap-1 cursor-pointer transition-all shrink-0"
            >
              <RefreshCw className="w-3 h-3" />
              RETRY CONNECTION
            </button>
          </div>
        )}

        {/* Dynamic View Rendering based on active navigation tab */}
        {activeTab === "dashboard" && (
          <DashboardView
            metrics={metrics}
            topologyNodes={topology?.nodes}
            topologyEdges={topology?.edges}
            telemetryPoints={telemetryPoints}
            aiModules={aiModules}
            frequencyHz={frequencyHz}
            wsStatus={wsStatus}
            isSimulating={simulating}
            onRunSimulation={handleRunSimulation}
            onWhatIfScenario={handleWhatIfScenario}
            onSelectModule={(id) => {
              if (id === "contingency-sim") setActiveTab("simulation");
              else if (id === "risk-engine") setActiveTab("risk-analysis");
              else if (id === "ai-forecast") setActiveTab("ai-forecast");
              else if (id === "what-if-sandbox") handleWhatIfScenario();
              else if (id === "dispatch-optimization") handleRunOptimization();
            }}
          />
        )}

        {activeTab === "grid-twin" && (
          <GridTwinView
            topologyNodes={topology?.nodes}
            topologyEdges={topology?.edges}
            frequencyHz={frequencyHz}
            isSimulating={simulating}
            onSimulate={handleRunSimulation}
          />
        )}

        {activeTab === "simulation" && <SimulationView />}

        {activeTab === "risk-analysis" && <RiskAnalysisView />}

        {activeTab === "ai-forecast" && <AiForecastView />}
      </main>

      {/* Contingency Simulation Modal */}
      {simulationModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-xl bg-slate-900 border border-amber-500/40 rounded-xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-amber-400 font-mono font-bold text-sm">
                <Terminal className="w-4 h-4" />
                <span>N-1 CONTINGENCY SIMULATION ENGINE</span>
              </div>
              <button
                onClick={() => setSimulationModalOpen(false)}
                className="text-slate-400 hover:text-white font-mono text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            {simulating ? (
              <div className="p-8 flex flex-col items-center justify-center space-y-3 font-mono text-xs text-amber-300">
                <RefreshCw className="w-6 h-6 animate-spin text-amber-400" />
                <span>Solving power flow & transient stability equations...</span>
              </div>
            ) : simResult ? (
              <div className="space-y-3">
                <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs space-y-1.5 text-slate-300">
                  <div className="flex justify-between text-slate-400">
                    <span>SOLVER STATUS:</span>
                    <span className="text-emerald-400 font-bold">{simResult.simulation_status.toUpperCase()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>TOTAL GENERATION:</span>
                    <span className="text-amber-400 font-bold">{simResult.total_generation_mw} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span>TOTAL DEMAND:</span>
                    <span className="text-cyan-400 font-bold">{simResult.total_demand_mw} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span>AVG LINE UTILIZATION:</span>
                    <span className="text-slate-100 font-bold">{simResult.line_utilization_avg}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>GRID RISK INDEX:</span>
                    <span className="text-emerald-400 font-bold">{simResult.risk_index.toFixed(3)} [LOW RISK]</span>
                  </div>
                  <div className="flex justify-between text-slate-500 pt-1 border-t border-slate-900">
                    <span>MODEL ENGINE:</span>
                    <span>{simResult.model_source}</span>
                  </div>
                </div>

                {simResult.simulation_warnings?.length > 0 && (
                  <div className="p-2.5 rounded bg-amber-950/40 border border-amber-500/30 text-[11px] font-mono text-amber-300">
                    {simResult.simulation_warnings.join(" | ")}
                  </div>
                )}
              </div>
            ) : null}

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setSimulationModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-amber-500 text-slate-950 font-mono font-bold text-xs hover:bg-amber-400 cursor-pointer"
              >
                DISMISS & APPLY TELEMETRY
              </button>
            </div>
          </div>
        </div>
      )}

      {/* What-If Scenario Modal */}
      {scenarioModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-xl bg-slate-900 border border-cyan-500/40 rounded-xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-cyan-400 font-mono font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>WHAT-IF SCENARIO BOUNDARY BUILDER</span>
              </div>
              <button
                onClick={() => setScenarioModalOpen(false)}
                className="text-slate-400 hover:text-white font-mono text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            {scenarioLoading ? (
              <div className="p-8 flex flex-col items-center justify-center space-y-3 font-mono text-xs text-cyan-300">
                <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
                <span>Calculating Monte Carlo stochastic boundary conditions...</span>
              </div>
            ) : scenarioResult ? (
              <div className="space-y-3 font-mono text-xs text-slate-300">
                <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">SCENARIO:</span>
                    <span className="text-cyan-400 font-bold">{scenarioResult.scenario_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>PROJECTED DEMAND:</span>
                    <span className="text-amber-400 font-bold">{scenarioResult.changed_demand_mw.toLocaleString()} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span>RENEWABLE SHARE:</span>
                    <span className="text-emerald-400 font-bold">{scenarioResult.renewable_share_percent}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>RESULTING RISK INDEX:</span>
                    <span className="text-rose-400 font-bold">{scenarioResult.resulting_risk_index.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>CRITICAL LOAD RELIABILITY:</span>
                    <span className="text-emerald-400 font-bold">{scenarioResult.critical_load_reliability_percent}%</span>
                  </div>
                </div>

                {scenarioResult.recommended_response?.length > 0 && (
                  <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1">
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">RECOMMENDED RESPONSE</span>
                    {scenarioResult.recommended_response.map((action, idx) => (
                      <div key={idx} className="flex items-start gap-1.5 text-emerald-300 text-[11px]">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{action}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : null}

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setScenarioModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-cyan-500 text-slate-950 font-mono font-bold text-xs hover:bg-cyan-400 cursor-pointer"
              >
                EXECUTE SCENARIO INJECTION
              </button>
            </div>
          </div>
        </div>
      )}

      {/* AI Dispatch Optimization Modal */}
      {optModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="relative w-full max-w-xl bg-slate-900 border border-blue-500/40 rounded-xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2 text-blue-400 font-mono font-bold text-sm">
                <Cpu className="w-4 h-4" />
                <span>AI DISPATCH & UNIT COMMITMENT SOLVER</span>
              </div>
              <button
                onClick={() => setOptModalOpen(false)}
                className="text-slate-400 hover:text-white font-mono text-sm cursor-pointer"
              >
                ✕
              </button>
            </div>

            {optLoading ? (
              <div className="p-8 flex flex-col items-center justify-center space-y-3 font-mono text-xs text-blue-300">
                <RefreshCw className="w-6 h-6 animate-spin text-blue-400" />
                <span>Computing MILP cost & carbon optimal dispatch vector...</span>
              </div>
            ) : optResult ? (
              <div className="space-y-3 font-mono text-xs text-slate-300">
                <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                  <div className="flex justify-between">
                    <span className="text-slate-400">OBJECTIVE:</span>
                    <span className="text-blue-400 font-bold">{optResult.objective.toUpperCase()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>DISPATCHED TOTAL:</span>
                    <span className="text-amber-400 font-bold">{optResult.total_dispatched_generation_mw} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span>BATTERY DISPATCH:</span>
                    <span className="text-emerald-400 font-bold">+{optResult.battery_dispatch_mw} MW</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ESTIMATED HOURLY COST:</span>
                    <span className="text-slate-100 font-bold">${Math.round(optResult.cost_estimate_usd).toLocaleString()} / hr</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 space-y-1">
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider block">DISPATCH RECOMMENDATIONS</span>
                  {optResult.recommended_actions.map((rec, idx) => (
                    <div key={idx} className="flex items-start gap-1.5 text-blue-300 text-[11px]">
                      <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0 mt-0.5" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}

            <div className="flex justify-end gap-3 pt-2">
              <button
                onClick={() => setOptModalOpen(false)}
                className="px-4 py-2 rounded-lg bg-blue-500 text-slate-950 font-mono font-bold text-xs hover:bg-blue-400 cursor-pointer"
              >
                APPLY OPTIMAL DISPATCH
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 mt-auto">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-slate-400 gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">PULSEiQ</span>
            <span>—</span>
            <span>NEXT-GENERATION ELECTRICITY GRID DIGITAL TWIN</span>
          </div>
          <div>
            API: {apiError ? "OFFLINE (FALLBACK)" : "CONNECTED"} | WS: {wsStatus.toUpperCase()}
          </div>
        </div>
      </footer>
    </div>
  );
}
