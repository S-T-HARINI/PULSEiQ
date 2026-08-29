"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/layout/Navbar";
import { HeroSection } from "@/components/dashboard/HeroSection";
import { CommandMetrics } from "@/components/dashboard/CommandMetrics";
import { GridTopologyFlow } from "@/components/grid/GridTopologyFlow";
import { TelemetryCharts } from "@/components/dashboard/TelemetryCharts";
import { AiSimulationModules } from "@/components/dashboard/AiSimulationModules";
import { gridMetricsData, simulationModulesData } from "@/lib/gridData";
import { Terminal, Sparkles } from "lucide-react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [simulationModalOpen, setSimulationModalOpen] = useState(false);
  const [scenarioModalOpen, setScenarioModalOpen] = useState(false);
  const [activeSimulationLog, setActiveSimulationLog] = useState<string | null>(null);

  const handleRunSimulation = () => {
    setSimulationModalOpen(true);
    setActiveSimulationLog("Initializing IEEE 118-bus transient stability scan...\nSimulating N-1 line trip on Branch 23-44...\nDynamic voltage stability index: 0.984 pu [SAFE]\nCascading overload probability: 0.002% [NEGLIGIBLE]\nDispatch redispatch recommendation: +25 MW BESS injection.\nSimulation complete in 184ms.");
  };

  const handleWhatIfScenario = () => {
    setScenarioModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col selection:bg-amber-500 selection:text-slate-950">
      {/* 1. Top Navigation */}
      <Navbar
        activeTab={activeTab}
        onTabChange={(tab) => setActiveTab(tab)}
        onRunSimulation={handleRunSimulation}
        onWhatIfScenario={handleWhatIfScenario}
      />

      {/* Main Content Container with guaranteed top padding so header never overlaps */}
      <main className="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-8 bg-tech-radial">
        {/* 2. Hero / Command Center Section */}
        <section aria-label="Command Center Hero">
          <HeroSection
            onRunSimulation={handleRunSimulation}
            onWhatIfScenario={handleWhatIfScenario}
          />
        </section>

        {/* 3. Grid Overview Command Metrics Strip */}
        <section aria-label="Grid Overview Metrics" className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
                SCADA TELEMETRY & SYSTEM HEALTH
              </h2>
            </div>
            <span className="text-[11px] font-mono text-slate-400 hidden sm:inline">
              LIVE SAMPLING: 50.02 Hz ± 0.02
            </span>
          </div>
          <CommandMetrics metrics={gridMetricsData} />
        </section>

        {/* 4. Main Grid Visualization (React Flow) & 5. Telemetry Charts (Recharts) */}
        <section className="grid grid-cols-1 xl:grid-cols-12 gap-6" aria-label="Topology & Telemetry">
          {/* Main Grid Visualization - Left/Top */}
          <div className="xl:col-span-7 space-y-2">
            <GridTopologyFlow />
          </div>

          {/* Telemetry Charts - Right/Bottom */}
          <div className="xl:col-span-5 space-y-2">
            <TelemetryCharts />
          </div>
        </section>

        {/* 6. AI & Simulation Modules */}
        <section aria-label="AI and Simulation Engines">
          <AiSimulationModules
            modules={simulationModulesData}
            onSelectModule={(id) => {
              if (id === "contingency-sim") handleRunSimulation();
              if (id === "what-if-sandbox") handleWhatIfScenario();
            }}
          />
        </section>
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

            <div className="p-3.5 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-emerald-400 whitespace-pre-wrap leading-relaxed">
              {activeSimulationLog}
            </div>

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

            <div className="space-y-3 font-mono text-xs text-slate-300">
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                <div className="flex justify-between">
                  <span>Scenario Preset:</span>
                  <span className="text-amber-400 font-bold">Heatwave Peak Surge (+18% Load)</span>
                </div>
                <div className="flex justify-between">
                  <span>Renewable Output Variance:</span>
                  <span className="text-cyan-400 font-bold">-25% Solar Cloud Transients</span>
                </div>
                <div className="flex justify-between">
                  <span>Storage Buffer Target:</span>
                  <span className="text-emerald-400 font-bold">95% BESS Dynamic Reserve</span>
                </div>
              </div>
              <p className="text-slate-400 font-sans text-xs">
                Ready to execute Monte Carlo multi-period stochastic simulation across all 148 grid substations.
              </p>
            </div>

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

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 mt-auto">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-slate-400 gap-2">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-300">PULSEiQ</span>
            <span>—</span>
            <span>NEXT-GENERATION ELECTRICITY GRID DIGITAL TWIN</span>
          </div>
          <div>SCADA / PMU NODE STATUS: SYNCHRONIZED</div>
        </div>
      </footer>
    </div>
  );
}
