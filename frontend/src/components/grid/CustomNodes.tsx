"use client";

import React from "react";
import { Handle, Position } from "@xyflow/react";
import { Sun, Wind, Zap, BatteryCharging, Building2 } from "lucide-react";

export interface NodeData {
  label: string;
  type: string;
  capacity?: string;
  output?: string;
  voltage?: string;
  status: "ONLINE" | "OPTIMAL" | "STANDBY" | "WARNING" | "SYNC";
  details?: string;
  load?: string;
  soc?: string;
}

export const SolarNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-amber-500/50 hover:border-amber-400 p-3 rounded-lg shadow-xl shadow-amber-500/10 w-[220px] transition-all">
      <div className="flex items-center justify-between gap-2 border-b border-amber-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Sun className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-wider text-amber-400">SOLAR ARRAY</div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[120px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
        </span>
      </div>

      <div className="space-y-1 text-[11px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-amber-400 font-semibold">{data.output || "850 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>CAPACITY:</span>
          <span className="text-slate-200">{data.capacity || "1,000 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>IRRADIANCE:</span>
          <span className="text-emerald-400">920 W/m²</span>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        id="solar-out"
        className="!w-3 !h-3 !bg-amber-400 !border-2 !border-slate-950"
      />
    </div>
  );
};

export const WindNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-cyan-500/50 hover:border-cyan-400 p-3 rounded-lg shadow-xl shadow-cyan-500/10 w-[220px] transition-all">
      <div className="flex items-center justify-between gap-2 border-b border-cyan-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Wind className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-wider text-cyan-400">WIND FARM</div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[120px]">{data.label}</div>
          </div>
        </div>
        <span className="flex h-2 w-2 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
        </span>
      </div>

      <div className="space-y-1 text-[11px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>OUTPUT:</span>
          <span className="text-cyan-400 font-semibold">{data.output || "620 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>WIND SPEED:</span>
          <span className="text-slate-200">11.8 m/s</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>TURBINES:</span>
          <span className="text-emerald-400">64 / 64 ACTIVE</span>
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        id="wind-out"
        className="!w-3 !h-3 !bg-cyan-400 !border-2 !border-slate-950"
      />
    </div>
  );
};

export const SubstationNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-slate-700 hover:border-amber-400/80 p-3.5 rounded-lg shadow-2xl w-[230px] transition-all">
      {/* Left Input Handle from Generators */}
      <Handle
        type="target"
        position={Position.Left}
        id="sub-left"
        className="!w-3 !h-3 !bg-blue-400 !border-2 !border-slate-950"
      />

      {/* Bottom Input Handle from BESS Storage */}
      <Handle
        type="target"
        position={Position.Bottom}
        id="sub-bottom"
        className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-slate-950"
      />
      
      <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-blue-500/10 border border-blue-500/30 text-blue-400">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-wider text-blue-400">400kV / 132kV SUBSTATION</div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[125px]">{data.label}</div>
          </div>
        </div>
        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-950/80 text-emerald-400 border border-emerald-800/50">
          {data.status || "SYNC"}
        </span>
      </div>

      <div className="space-y-1 text-[11px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>THROUGHPUT:</span>
          <span className="text-slate-100 font-semibold">{data.output || "1,840 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>BUS VOLTAGE:</span>
          <span className="text-emerald-400">{data.voltage || "401.2 kV"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>STABILITY:</span>
          <span className="text-amber-400">99.4% (N-1 Safe)</span>
        </div>
      </div>

      {/* Right Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        id="sub-right"
        className="!w-3 !h-3 !bg-amber-400 !border-2 !border-slate-950"
      />
    </div>
  );
};

export const BatteryNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-emerald-500/50 hover:border-emerald-400 p-3 rounded-lg shadow-xl shadow-emerald-500/10 w-[220px] transition-all">
      <div className="flex items-center justify-between gap-2 border-b border-emerald-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <BatteryCharging className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-wider text-emerald-400">BESS STORAGE</div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[120px]">{data.label}</div>
          </div>
        </div>
        <span className="text-[9px] font-mono text-emerald-400 font-bold px-1 rounded bg-emerald-950/60 border border-emerald-800/40">
          DISCHARGE
        </span>
      </div>

      <div className="space-y-1 text-[11px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>POWER FLOW:</span>
          <span className="text-emerald-400 font-semibold">+180 MW</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>STATE OF CHARGE:</span>
          <span className="text-slate-100">{data.soc || "84.5%"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>CYCLE EFFICIENCY:</span>
          <span className="text-slate-300">94.2%</span>
        </div>
      </div>

      {/* Top Source Handle to Substation Bottom */}
      <Handle
        type="source"
        position={Position.Top}
        id="bess-out"
        className="!w-3 !h-3 !bg-emerald-400 !border-2 !border-slate-950"
      />
    </div>
  );
};

export const CityLoadNode: React.FC<{ data: NodeData }> = ({ data }) => {
  return (
    <div className="relative group bg-slate-900/95 backdrop-blur-md border border-rose-500/50 hover:border-rose-400 p-3.5 rounded-lg shadow-2xl shadow-rose-500/10 w-[230px] transition-all">
      <Handle
        type="target"
        position={Position.Left}
        id="city-in"
        className="!w-3 !h-3 !bg-rose-400 !border-2 !border-slate-950"
      />

      <div className="flex items-center justify-between gap-2 border-b border-rose-500/20 pb-2 mb-2">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-400">
            <Building2 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[9px] font-mono uppercase tracking-wider text-rose-400">METRO LOAD SINK</div>
            <div className="text-xs font-bold text-slate-100 truncate max-w-[125px]">{data.label}</div>
          </div>
        </div>
        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-rose-950/80 text-rose-400 border border-rose-800/50">
          DEMAND
        </span>
      </div>

      <div className="space-y-1 text-[11px] font-mono">
        <div className="flex justify-between text-slate-400">
          <span>ACTIVE DEMAND:</span>
          <span className="text-rose-400 font-semibold">{data.load || "2,420 MW"}</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>POWER FACTOR:</span>
          <span className="text-slate-200">0.98 lag</span>
        </div>
        <div className="flex justify-between text-slate-400">
          <span>RELIABILITY:</span>
          <span className="text-emerald-400">99.998% SAIDI</span>
        </div>
      </div>
    </div>
  );
};
