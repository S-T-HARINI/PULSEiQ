"use client";

import React from "react";
import { SimulationModule } from "@/types/grid";
import {
  Cpu,
  ShieldAlert,
  Sliders,
  Zap,
  Activity,
  ArrowUpRight,
  CheckCircle2,
} from "lucide-react";

interface AiSimulationModulesProps {
  modules: SimulationModule[];
  onSelectModule?: (moduleId: string) => void;
}

export const AiSimulationModules: React.FC<AiSimulationModulesProps> = ({
  modules,
  onSelectModule,
}) => {
  const getIcon = (id: string) => {
    switch (id) {
      case "ai-forecast":
        return <Cpu className="w-5 h-5 text-cyan-400" />;
      case "contingency-sim":
        return <ShieldAlert className="w-5 h-5 text-amber-400" />;
      case "what-if-sandbox":
        return <Sliders className="w-5 h-5 text-emerald-400" />;
      case "dispatch-optimization":
        return <Zap className="w-5 h-5 text-blue-400" />;
      case "scada-stream":
        return <Activity className="w-5 h-5 text-emerald-400" />;
      default:
        return <Cpu className="w-5 h-5 text-slate-400" />;
    }
  };

  const getAccentBorder = (color: string) => {
    switch (color) {
      case "amber":
        return "hover:border-amber-500/60 hover:shadow-[0_10px_30px_rgba(245,158,11,0.15)]";
      case "cyan":
        return "hover:border-cyan-500/60 hover:shadow-[0_10px_30px_rgba(6,182,212,0.15)]";
      case "emerald":
        return "hover:border-emerald-500/60 hover:shadow-[0_10px_30px_rgba(16,185,129,0.15)]";
      case "blue":
        return "hover:border-blue-500/60 hover:shadow-[0_10px_30px_rgba(59,130,246,0.15)]";
      default:
        return "hover:border-slate-600 hover:shadow-[0_10px_30px_rgba(0,0,0,0.4)]";
    }
  };

  const getTopGlow = (color: string) => {
    switch (color) {
      case "amber":
        return "from-amber-500/80 to-yellow-500/80";
      case "cyan":
        return "from-cyan-500/80 to-blue-500/80";
      case "emerald":
        return "from-emerald-500/80 to-teal-500/80";
      case "blue":
        return "from-blue-500/80 to-indigo-500/80";
      default:
        return "from-slate-600 to-slate-700";
    }
  };

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.15)]">
            <Cpu className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-base font-bold font-mono text-slate-100 uppercase tracking-tight">
              AI ENGINES & SIMULATION MODULES
            </h2>
            <p className="text-xs text-slate-400 font-sans">
              Autonomous grid stability agents, predictive neural models, and optimization algorithms.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-xs font-mono text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>5/5 ENGINES READY</span>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {modules.map((mod) => (
          <div
            key={mod.id}
            className={`group relative bg-[#090d16]/90 border border-slate-800/90 rounded-2xl p-5 flex flex-col justify-between shadow-xl backdrop-blur-2xl transition-all duration-200 cursor-pointer hover:-translate-y-1 overflow-hidden ${getAccentBorder(
              mod.accentColor
            )}`}
            onClick={() => onSelectModule && onSelectModule(mod.id)}
          >
            {/* Top Accent Line */}
            <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${getTopGlow(mod.accentColor)} opacity-75 group-hover:opacity-100 transition-opacity`} />

            <div>
              {/* Header: Icon & Status Tag */}
              <div className="flex items-center justify-between gap-2 mb-3 pt-0.5">
                <div className="p-2 rounded-xl bg-slate-900/90 border border-slate-800 shadow-inner group-hover:border-slate-700 transition-colors">
                  {getIcon(mod.id)}
                </div>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                  <CheckCircle2 className="w-2.5 h-2.5" />
                  {mod.status}
                </span>
              </div>

              {/* Tag & Title */}
              <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 mb-1">
                {mod.tag}
              </div>
              <h3 className="text-sm font-bold text-slate-100 group-hover:text-amber-300 transition-colors font-mono line-clamp-2">
                {mod.name}
              </h3>

              {/* Description */}
              <p className="mt-2 text-xs text-slate-400 line-clamp-3 leading-relaxed font-sans font-normal">
                {mod.description}
              </p>
            </div>

            {/* Stats & Action Footer */}
            <div className="mt-4 pt-3.5 border-t border-slate-800/80 space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                {mod.stats.map((stat, i) => (
                  <div key={i} className="p-2 rounded-lg bg-slate-900/80 border border-slate-800/80 shadow-xs">
                    <span className="text-slate-500 text-[9px] uppercase tracking-wider block">{stat.label}</span>
                    <span className="text-slate-100 font-bold">{stat.value}</span>
                  </div>
                ))}
              </div>

              <button
                className="w-full py-2.5 px-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 group-hover:border-amber-500/50 text-xs font-mono font-bold text-slate-300 group-hover:text-amber-300 flex items-center justify-center gap-1.5 transition-all shadow-xs"
              >
                <span>{mod.actionLabel}</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform text-amber-400" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
