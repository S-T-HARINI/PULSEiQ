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

  const getBorderColor = (id: string, status: string) => {
    if (id === "active-alerts" && status === "warning") return "hover:border-amber-500/50";
    if (status === "optimal") return "hover:border-emerald-500/50";
    return "hover:border-slate-600";
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-3">
      {metrics.map((metric) => (
        <div
          key={metric.id}
          className={`relative group bg-slate-950/80 border border-slate-800/90 rounded-xl p-3.5 flex flex-col justify-between shadow-xl backdrop-blur-md transition-all duration-200 ${getBorderColor(
            metric.id,
            metric.status
          )}`}
        >
          {/* Top Label & Icon */}
          <div className="flex items-center justify-between gap-1 mb-2">
            <span className="text-[10px] font-mono font-bold tracking-wider text-slate-400 uppercase truncate">
              {metric.label}
            </span>
            <div className="p-1 rounded bg-slate-900 border border-slate-800/80 shrink-0">
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
          <div className="pt-2 mt-1 border-t border-slate-900/80 flex items-center justify-between text-[10px] font-mono">
            {metric.delta && (
              <span
                className={`font-semibold ${
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
            <span className="text-slate-400 truncate ml-1 text-right max-w-[90px]" title={metric.technicalDetail}>
              {metric.technicalDetail}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};
