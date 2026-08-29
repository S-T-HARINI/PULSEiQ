"use client";

import React from "react";
import { GridTopologyFlow } from "@/components/grid/GridTopologyFlow";
import { Node, Edge } from "@xyflow/react";
import { Network, Zap, Activity, ShieldCheck, Radio } from "lucide-react";

interface GridTwinViewProps {
  topologyNodes?: Node[];
  topologyEdges?: Edge[];
  frequencyHz: number;
  isSimulating: boolean;
  onSimulate: () => void;
}

export const GridTwinView: React.FC<GridTwinViewProps> = ({
  topologyNodes,
  topologyEdges,
  frequencyHz,
  isSimulating,
  onSimulate,
}) => {
  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="rounded-2xl border border-slate-800 bg-slate-950/90 p-6 backdrop-blur-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Network className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold font-mono text-slate-100 uppercase tracking-tight">
                DIGITAL TWIN TOPOLOGY & SUBSTATION SCADA
              </h1>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                ACTIVE MULTI-BUS
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Real-time synchronization with 400kV/220kV transmission substations, distributed generation nodes, and BESS reserves.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-emerald-400">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>SUB-SECOND PMU: 50.02 Hz</span>
          </div>
        </div>
      </div>

      {/* Main Full-Height React Flow Grid Topology */}
      <div className="w-full">
        <GridTopologyFlow
          nodes={topologyNodes}
          edges={topologyEdges}
          frequencyHz={frequencyHz}
          isSimulating={isSimulating}
          onSimulate={onSimulate}
        />
      </div>

      {/* Asset Status & Operational Telemetry Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-900">
            <span className="flex items-center gap-1.5">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>TOTAL CAPACITY & HEADROOM</span>
            </span>
            <span className="text-emerald-400 font-bold">ONLINE</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Nameplate Capacity:</span>
            <span className="text-slate-100 font-bold">4,850 MW</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Current Active Load:</span>
            <span className="text-cyan-400 font-bold">3,780 MW</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Available Spinning Reserve:</span>
            <span className="text-emerald-400 font-bold">+1,070 MW</span>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-900">
            <span className="flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>BUSBAR FREQUENCY & VOLTAGE</span>
            </span>
            <span className="text-cyan-400 font-bold">NOMINAL</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">System Frequency:</span>
            <span className="text-slate-100 font-bold">{frequencyHz.toFixed(2)} Hz</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Hub Bus Voltage:</span>
            <span className="text-emerald-400 font-bold">401.2 kV (1.003 pu)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Metro Bus Voltage:</span>
            <span className="text-emerald-400 font-bold">220.8 kV (1.004 pu)</span>
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/80 p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400 pb-2 border-b border-slate-900">
            <span className="flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
              <span>N-1 RELIABILITY & STABILITY</span>
            </span>
            <span className="text-emerald-400 font-bold">STABLE</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Grid Stability Index:</span>
            <span className="text-slate-100 font-bold">98.6%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Active Contingencies:</span>
            <span className="text-slate-100 font-bold">0 Outages</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Inertia Constant (H):</span>
            <span className="text-amber-400 font-bold">4.82 s (Secure)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
