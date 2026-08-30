"use client";

import React from "react";
import { GridMetric } from "@/types/grid";
import {
  Zap,
  Activity,
  ShieldCheck,
  Radio,
  Gauge,
  AlertTriangle,
  Building,
} from "lucide-react";

interface CommandMetricsProps {
  metrics: GridMetric[];
}

export const CommandMetrics: React.FC<CommandMetricsProps> = ({ metrics }) => {
  const getIcon = (id: string) => {
    switch (id) {
      case "active-substations":
        return <Building className="w-4 h-4 text-blue-400" />;
      case "total-capacity":
        return <Zap className="w-4 h-4 text-amber-400" />;
      case "current-load":
        return <Gauge className="w-4 h-4 text-cyan-400" />;
      case "load-factor":
        return <Activity className="w-4 h-4 text-emerald-400" />;
      case "stability-index":
        return <ShieldCheck className="w-4 h-4 text-indigo-400" />;
      case "grid-frequency":
        return <Radio className="w-4 h-4 text-cyan-400" />;
      case "active-alerts":
        return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default:
        return <Activity className="w-4 h-4 text-slate-400" />;
    }
  };

  const getAccentGlow = (id: string, status: string) => {
    if (id === "active-alerts" && status === "warning") return "from-rose-500/80 to-amber-500/80";
    if (id === "grid-frequency") return "from-cyan-500/80 to-blue-500/80";
    if (id === "stability-index") return "from-indigo-500/80 to-purple-500/80";
    if (id === "total-capacity") return "from-amber-500/80 to-yellow-500/80";
    if (id === "current-load") return "from-cyan-500/80 to-emerald-500/80";
    if (status === "optimal") return "from-emerald-500/80 to-teal-500/80";
    return "from-slate-600 to-slate-700";
  };

  const getBorderColor = (id: string, status: string) => {
    if (id === "active-alerts" && status === "warning") return "hover:border-rose-500/50";
    if (status === "warning") return "hover:border-amber-500/50";
    if (status === "optimal") return "hover:border-emerald-500/50";
    return "hover:border-cyan-500/50";
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
      {metrics.map((metric) => (
        <div
          key={metric.id}
          className={`relative group bg-[#090d16]/90 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between shadow-xl backdrop-blur-xl transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_25px_rgba(0,0,0,0.5)] overflow-hidden ${getBorderColor(
            metric.id,
            metric.status
          )}`}
        >
          {/* Glowing Top Accent Line */}
          <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${getAccentGlow(metric.id, metric.status)} opacity-75 group-hover:opacity-100 transition-opacity`} />

          {/* Top Label & Icon */}
          <div className="flex items-center justify-between gap-1 mb-2 pt-0.5">
            <span className="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase truncate">
              {metric.label}
            </span>
            <div className="p-1 rounded-lg bg-slate-900/90 border border-slate-800 shrink-0 shadow-inner group-hover:border-slate-700 transition-colors">
              {getIcon(metric.id)}
            </div>
          </div>

          {/* Metric Value & Unit */}
          <div className="flex items-baseline gap-1.5 my-1">
            <span className="text-xl sm:text-2xl font-black font-mono tracking-tight text-slate-100">
              {metric.value}
            </span>
            {metric.unit && (
              <span className="text-[10px] font-mono font-bold text-slate-400">
                {metric.unit}
              </span>
            )}
          </div>

          {/* Delta & Technical Detail */}
          <div className="pt-2 mt-1.5 border-t border-slate-800/60 flex items-center justify-between text-[10px] font-mono">
            {metric.delta && (
              <span
                className={`font-semibold flex items-center gap-1 ${
                  metric.deltaType === "positive"
                    ? "text-emerald-400"
                    : metric.deltaType === "negative"
                    ? "text-rose-400"
                    : "text-amber-400"
                }`}
              >
                {metric.delta}
              </span>
            )}
            <span className="text-slate-400 truncate ml-1 text-right max-w-[95px]" title={metric.technicalDetail}>
              {metric.technicalDetail}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
