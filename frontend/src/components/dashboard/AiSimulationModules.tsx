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
        return "hover:border-amber-500/50 hover:shadow-amber-500/10";
      case "cyan":
        return "hover:border-cyan-500/50 hover:shadow-cyan-500/10";
      case "emerald":
        return "hover:border-emerald-500/50 hover:shadow-emerald-500/10";
      case "blue":
        return "hover:border-blue-500/50 hover:shadow-blue-500/10";
      default:
        return "hover:border-slate-600";
    }
  };

  return (
    <div className="space-y-4">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
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
        <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>5/5 ENGINES READY</span>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {modules.map((mod) => (
          <div
            key={mod.id}
            className={`group relative bg-slate-950/90 border border-slate-800 rounded-xl p-4.5 flex flex-col justify-between shadow-xl backdrop-blur-xl transition-all duration-200 cursor-pointer ${getAccentBorder(
              mod.accentColor
            )}`}
            onClick={() => onSelectModule && onSelectModule(mod.id)}
          >
            <div>
              {/* Header: Icon & Status Tag */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  {getIcon(mod.id)}
                </div>
                <span className="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-slate-900 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
                  <CheckCircle2 className="w-2.5 h-2.5" />
                  {mod.status}
                </span>
              </div>

              {/* Tag & Title */}
              <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500 mb-1">
                {mod.tag}
              </div>
              <h3 className="text-sm font-bold text-slate-100 group-hover:text-amber-400 transition-colors font-mono line-clamp-2">
                {mod.name}
              </h3>

              {/* Description */}
              <p className="mt-2 text-xs text-slate-400 line-clamp-3 leading-relaxed font-sans">
                {mod.description}
              </p>
            </div>

            {/* Stats & Action Footer */}
            <div className="mt-4 pt-3 border-t border-slate-900/90 space-y-3">
              <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
                {mod.stats.map((stat, i) => (
                  <div key={i} className="p-1.5 rounded bg-slate-900/60 border border-slate-800/80">
                    <span className="text-slate-500 block">{stat.label}</span>
                    <span className="text-slate-200 font-bold">{stat.value}</span>
                  </div>
                ))}
              </div>

              <button
                className="w-full py-2 px-3 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 group-hover:border-amber-500/40 text-xs font-mono font-bold text-slate-300 group-hover:text-amber-300 flex items-center justify-center gap-1.5 transition-all"
              >
                <span>{mod.actionLabel}</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
