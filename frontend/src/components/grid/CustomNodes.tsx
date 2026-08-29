"use client";

import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Sun, Wind, Zap, BatteryCharging, Building2, Flame, ShieldAlert, Cpu } from "lucide-react";

export interface NodeData {
  label: string;
  type: string;
  capacity?: string;
  output?: string;
  voltage?: string;
  status: "ONLINE" | "OPTIMAL" | "STANDBY" | "WARNING" | "SYNC" | "CRITICAL";
  details?: string;
  load?: string;
  soc?: string;
  subType?: string;
  criticality?: string;
}

export const SolarNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-amber-500/50 hover:border-amber-400 p-3 rounded-lg shadow-xl shadow-amber-500/10 w-[210px] transition-all">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-amber-500/20 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Sun className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-amber-400">SOLAR PV</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-1.5 w-1.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-amber-500"></span>
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-amber-400 font-semibold">{data.output || "450 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>CAPACITY:</span>
          <span className="text-slate-200">{data.capacity || "500 MW"}</span>
        </div>
      </div>
    </div>
  );
};

export const WindNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-cyan-500/50 hover:border-cyan-400 p-3 rounded-lg shadow-xl shadow-cyan-500/10 w-[210px] transition-all">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-2.5 !h-2.5 !bg-cyan-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-cyan-500/20 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Wind className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-cyan-400">WIND FARM</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-1.5 w-1.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-cyan-500"></span>
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-cyan-400 font-semibold">{data.output || "380 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>CAPACITY:</span>
          <span className="text-slate-200">{data.capacity || "450 MW"}</span>
        </div>
      </div>
    </div>
  );
};

export const ThermalNode: React.FC<{ data: NodeData }> = ({ data }) => {
  const isNuclear = data.label?.toLowerCase().includes("nuclear");
  const isHydro = data.label?.toLowerCase().includes("hydro");
  const badgeText = isNuclear ? "NUCLEAR" : isHydro ? "HYDRO" : "THERMAL / GAS";
  const badgeColor = isNuclear ? "text-emerald-400 border-emerald-800 bg-emerald-950" : "text-orange-400 border-orange-800 bg-orange-950";

  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-orange-500/50 hover:border-orange-400 p-3 rounded-lg shadow-xl shadow-orange-500/10 w-[210px] transition-all">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-2.5 !h-2.5 !bg-orange-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-orange-500/20 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400">
            <Flame className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-orange-400">{badgeText}</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className={`px-1 py-0.2 rounded text-[8px] font-mono font-bold border ${badgeColor}`}>
          SYNC
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>DISPATCH:</span>
          <span className="text-orange-400 font-semibold">{data.output || "650 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>CAPACITY:</span>
          <span className="text-slate-200">{data.capacity || "700 MW"}</span>
        </div>
      </div>
    </div>
  );
};

export const SubstationNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-slate-700 hover:border-amber-400/80 p-3 rounded-lg shadow-2xl w-[220px] transition-all">
      <Handle type="target" position={Position.Left} id="left" className="!w-2.5 !h-2.5 !bg-blue-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-2.5 !h-2.5 !bg-blue-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Right} id="right-in" className="!w-2.5 !h-2.5 !bg-blue-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Left} id="left-out" className="!w-2.5 !h-2.5 !bg-amber-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-400">
            <Zap className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-blue-400">SUBSTATION</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[115px]">{data.label}</div>
          </div>
        </div>
        <span className="px-1 py-0.2 rounded text-[8px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
          {data.status || "SYNC"}
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>FLOW:</span>
          <span className="text-slate-100 font-semibold">{data.output || "1,240 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>VOLTAGE:</span>
          <span className="text-emerald-400">{data.voltage || "400.0 kV"}</span>
        </div>
      </div>
    </div>
  );
};

export const BatteryNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-emerald-500/50 hover:border-emerald-400 p-3 rounded-lg shadow-xl shadow-emerald-500/10 w-[210px] transition-all">
      <Handle type="target" position={Position.Left} id="left" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Left} id="left-out" className="!w-2.5 !h-2.5 !bg-emerald-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-emerald-500/20 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <BatteryCharging className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-emerald-400">BESS STORAGE</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="text-[8px] font-mono text-emerald-400 font-bold px-1 rounded bg-emerald-950/60 border border-emerald-800/40">
          ACTIVE
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>FLOW:</span>
          <span className="text-emerald-400 font-semibold">{data.output || "+150 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>SOC:</span>
          <span className="text-slate-100">{data.soc || "88.2%"}</span>
        </div>
      </div>
    </div>
  );
};

export const CityLoadNode: React.FC<{ data: NodeData }> = ({ data }) => {
  const isCritical = data.label?.toLowerCase().includes("hospital") || data.label?.toLowerCase().includes("trauma") || data.label?.toLowerCase().includes("datacenter") || data.label?.toLowerCase().includes("supercluster");
  const isAI = data.label?.toLowerCase().includes("supercluster") || data.label?.toLowerCase().includes("gpu");

  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-rose-500/50 hover:border-rose-400 p-3 rounded-lg shadow-2xl shadow-rose-500/10 w-[210px] transition-all">
      <Handle type="target" position={Position.Left} id="left" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Top} id="top" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Bottom} id="bottom" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />
      <Handle type="target" position={Position.Right} id="right-in" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Right} id="right" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />
      <Handle type="source" position={Position.Bottom} id="bottom-out" className="!w-2.5 !h-2.5 !bg-rose-400 !border-2 !border-slate-950" />

      <div className="flex items-center justify-between gap-2 border-b border-rose-500/20 pb-1.5 mb-1.5">
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400">
            {isAI ? <Cpu className="w-3.5 h-3.5" /> : isCritical ? <ShieldAlert className="w-3.5 h-3.5" /> : <Building2 className="w-3.5 h-3.5" />}
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-rose-400">
              {isCritical ? "CRITICAL LOAD" : "LOAD SINK"}
            </div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className={`px-1 py-0.2 rounded text-[8px] font-mono font-bold border ${isCritical ? "bg-amber-950/90 text-amber-400 border-amber-800" : "bg-rose-950/80 text-rose-400 border-rose-800/50"}`}>
          {isCritical ? "TIER-1" : "DEMAND"}
        </span>
      </div>

      <div className="space-y-0.5 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>DEMAND:</span>
          <span className="text-rose-400 font-semibold">{data.load || data.output || "420 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>PRIORITY:</span>
          <span className={isCritical ? "text-amber-400 font-bold" : "text-emerald-400"}>
            {isCritical ? "UNINTERRUPTIBLE" : "TIER-1 SECURE"}
          </span>
        </div>
      </div>
    </div>
  );
};
