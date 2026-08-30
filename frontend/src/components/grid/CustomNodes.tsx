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
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-amber-500/50 hover:border-amber-400 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(245,158,11,0.15)] hover:shadow-[0_12px_35px_rgba(245,158,11,0.3)] w-[215px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-amber-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-inner">
            <Sun className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-amber-400 font-bold">SOLAR PV</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-amber-400 font-bold">{data.output || "450 MW"}</span>
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
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-cyan-500/50 hover:border-cyan-400 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(6,182,212,0.15)] hover:shadow-[0_12px_35px_rgba(6,182,212,0.3)] w-[215px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-cyan-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-inner">
            <Wind className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-cyan-400 font-bold">WIND FARM</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-cyan-400 font-bold">{data.output || "380 MW"}</span>
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
  const badgeColor = isNuclear ? "text-emerald-400 border-emerald-700 bg-emerald-950/80" : "text-orange-400 border-orange-700 bg-orange-950/80";

  return (
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-orange-500/50 hover:border-orange-400 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(249,115,22,0.15)] hover:shadow-[0_12px_35px_rgba(249,115,22,0.3)] w-[215px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left-in" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-3 !h-3 !bg-orange-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-orange-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-orange-500/10 border border-orange-500/30 text-orange-400 shadow-inner">
            <Flame className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-orange-400 font-bold">{badgeText}</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className={`px-1.5 py-0.5 rounded text-[8px] font-mono font-bold border shadow-xs ${badgeColor}`}>
          SYNC
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>DISPATCH:</span>
          <span className="text-orange-400 font-bold">{data.output || "650 MW"}</span>
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
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-slate-700 hover:border-amber-400/90 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.5)] hover:shadow-[0_12px_35px_rgba(59,130,246,0.25)] w-[225px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left" className="!w-3 !h-3 !bg-blue-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-3 !h-3 !bg-blue-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Right} id="right-in" className="!w-3 !h-3 !bg-blue-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Left} id="left-out" className="!w-3 !h-3 !bg-amber-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/30 text-blue-400 shadow-inner">
            <Zap className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-blue-400 font-bold">SUBSTATION</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[115px]">{data.label}</div>
          </div>
        </div>
        <span className="px-1.5 py-0.5 rounded text-[8px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-700/60 shadow-xs">
          {data.status || "SYNC"}
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>FLOW:</span>
          <span className="text-slate-100 font-bold">{data.output || "1,240 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>VOLTAGE:</span>
          <span className="text-emerald-400 font-semibold">{data.voltage || "400.0 kV"}</span>
        </div>
      </div>
    </div>
  );
};

export const BatteryNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-emerald-500/50 hover:border-emerald-400 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(16,185,129,0.15)] hover:shadow-[0_12px_35px_rgba(16,185,129,0.3)] w-[215px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top-in" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom-in" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Left} id="left-out" className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-emerald-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 shadow-inner">
            <BatteryCharging className="w-3.5 h-3.5" />
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-emerald-400 font-bold">BESS STORAGE</div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className="text-[8px] font-mono text-emerald-400 font-bold px-1.5 py-0.5 rounded bg-emerald-950/70 border border-emerald-700/60 shadow-xs">
          ACTIVE
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>FLOW:</span>
          <span className="text-emerald-400 font-bold">{data.output || "+150 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>SOC:</span>
          <span className="text-slate-100 font-semibold">{data.soc || "88.2%"}</span>
        </div>
      </div>
    </div>
  );
};

export const CityLoadNode: React.FC<{ data: NodeData }> = ({ data }) => {
  const isCritical = data.label?.toLowerCase().includes("hospital") || data.label?.toLowerCase().includes("trauma") || data.label?.toLowerCase().includes("datacenter") || data.label?.toLowerCase().includes("supercluster");
  const isAI = data.label?.toLowerCase().includes("supercluster") || data.label?.toLowerCase().includes("gpu");

  return (
    <div className="relative group bg-[#090d16]/95 backdrop-blur-xl border border-rose-500/50 hover:border-rose-400 p-3.5 rounded-xl shadow-[0_10px_30px_rgba(244,63,94,0.15)] hover:shadow-[0_12px_35px_rgba(244,63,94,0.3)] w-[215px] transition-all duration-200">
      <Handle type="target" position={Position.Left} id="left" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Top} id="top" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Bottom} id="bottom" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="target" position={Position.Right} id="right-in" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Right} id="right" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Bottom} id="bottom-out" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Left} id="left-out" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />
      <Handle type="source" position={Position.Top} id="top-out" className="!w-3 !h-3 !bg-rose-400 !border-2 !border-[#090d16]" />

      <div className="flex items-center justify-between gap-2 border-b border-rose-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 shadow-inner">
            {isAI ? <Cpu className="w-3.5 h-3.5" /> : isCritical ? <ShieldAlert className="w-3.5 h-3.5" /> : <Building2 className="w-3.5 h-3.5" />}
          </div>
          <div>
            <div className="text-[8px] font-mono uppercase tracking-wider text-rose-400 font-bold">
              {isCritical ? "CRITICAL LOAD" : "LOAD SINK"}
            </div>
            <div className="text-[11px] font-bold text-slate-100 truncate max-w-[110px]">{data.label}</div>
          </div>
        </div>
        <span className={`px-1.5 py-0.5 rounded text-[8px] font-mono font-bold border shadow-xs ${isCritical ? "bg-amber-950/90 text-amber-400 border-amber-700/80" : "bg-rose-950/80 text-rose-400 border-rose-700/80"}`}>
          {isCritical ? "TIER-1" : "DEMAND"}
        </span>
      </div>

      <div className="space-y-1 text-[10px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>DEMAND:</span>
          <span className="text-rose-400 font-bold">{data.load || data.output || "420 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>PRIORITY:</span>
          <span className={isCritical ? "text-amber-400 font-bold" : "text-emerald-400 font-medium"}>
            {isCritical ? "UNINTERRUPTIBLE" : "TIER-1 SECURE"}
          </span>
        </div>
      </div>
    </div>
  );
};
