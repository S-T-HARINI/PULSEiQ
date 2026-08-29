"use client";

import React from "react";
import { HeroSection } from "@/components/dashboard/HeroSection";
import { CommandMetrics } from "@/components/dashboard/CommandMetrics";
import { GridTopologyFlow } from "@/components/grid/GridTopologyFlow";
import { TelemetryCharts } from "@/components/dashboard/TelemetryCharts";
import { AiSimulationModules } from "@/components/dashboard/AiSimulationModules";
import { GridMetric, TelemetryPoint, SimulationModule } from "@/types/grid";
import { Node, Edge } from "@xyflow/react";

interface DashboardViewProps {
  metrics: GridMetric[];
  topologyNodes?: Node[];
  topologyEdges?: Edge[];
  telemetryPoints: TelemetryPoint[];
  aiModules: SimulationModule[];
  frequencyHz: number;
  wsStatus: string;
  isSimulating: boolean;
  onRunSimulation: () => void;
  onWhatIfScenario: () => void;
  onSelectModule: (id: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  metrics,
  topologyNodes,
  topologyEdges,
  telemetryPoints,
  aiModules,
  frequencyHz,
  wsStatus,
  isSimulating,
  onRunSimulation,
  onWhatIfScenario,
  onSelectModule,
}) => {
  return (
    <div className="space-y-8">
      {/* Hero / Command Center Section */}
      <section aria-label="Command Center Hero">
        <HeroSection
          onRunSimulation={onRunSimulation}
          onWhatIfScenario={onWhatIfScenario}
        />
      </section>

      {/* Grid Overview Command Metrics Strip */}
      <section aria-label="Grid Overview Metrics" className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
              SCADA TELEMETRY & SYSTEM HEALTH
            </h2>
          </div>
          <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
            <span className="hidden sm:inline">
              STREAM: {wsStatus === "connected" ? "LIVE WEBSOCKET" : "REST SYNC"}
            </span>
            <span>SAMPLING: {frequencyHz.toFixed(2)} Hz</span>
          </div>
        </div>
        <CommandMetrics metrics={metrics} />
      </section>

      {/* Side-by-side Overview: Grid Topology + Telemetry Charts */}
      <section className="grid grid-cols-1 xl:grid-cols-12 gap-6" aria-label="Topology & Telemetry">
        <div className="xl:col-span-7 space-y-2">
          <GridTopologyFlow
            nodes={topologyNodes}
            edges={topologyEdges}
            frequencyHz={frequencyHz}
            isSimulating={isSimulating}
            onSimulate={onRunSimulation}
          />
        </div>
        <div className="xl:col-span-5 space-y-2">
          <TelemetryCharts telemetryData={telemetryPoints} />
        </div>
      </section>

      {/* AI & Simulation Modules Overview */}
      <section aria-label="AI and Simulation Engines">
        <AiSimulationModules
          modules={aiModules}
          onSelectModule={onSelectModule}
        />
      </section>
    </div>
  );
};
