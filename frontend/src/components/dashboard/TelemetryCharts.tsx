"use client";

import React, { useState } from "react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";
import { telemetry24hData as defaultTelemetry } from "@/lib/gridData";
import { TelemetryPoint } from "@/types/grid";
import { Activity } from "lucide-react";

interface TelemetryChartsProps {
  telemetryData?: TelemetryPoint[];
}

export const TelemetryCharts: React.FC<TelemetryChartsProps> = ({
  telemetryData = defaultTelemetry,
}) => {
  const [activeTab, setActiveTab] = useState<"load-gen" | "frequency" | "generation-mix">("load-gen");

  const chartData = telemetryData && telemetryData.length > 0 ? telemetryData : defaultTelemetry;

  // Compute summary stats dynamically from active telemetry
  const peakPoint = chartData.reduce(
    (max, p) => (p.loadMW > max.loadMW ? p : max),
    chartData[0] || { time: "18:00", loadMW: 4600 }
  );

  const maxRenewablePercent = chartData.reduce((max, p) => {
    const total = p.solarMW + p.windMW + p.bessMW + p.thermalMW;
    const ren = total > 0 ? ((p.solarMW + p.windMW) / total) * 100 : 0;
    return ren > max ? ren : max;
  }, 0);

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/90 shadow-2xl p-5 backdrop-blur-xl space-y-4">
      {/* Header & Mode Switcher */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100 font-mono tracking-tight">
                REAL-TIME TELEMETRY & SCADA ANALYTICS
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                LIVE STREAM
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Phasor measurement unit (PMU) 24-hour telemetry curves, frequency variance, and dispatch curves.
            </p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800 rounded-lg self-start sm:self-auto">
          <button
            onClick={() => setActiveTab("load-gen")}
            className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all cursor-pointer ${
              activeTab === "load-gen"
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            LOAD VS GEN
          </button>
          <button
            onClick={() => setActiveTab("frequency")}
            className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all cursor-pointer ${
              activeTab === "frequency"
                ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            FREQUENCY (Hz)
          </button>
          <button
            onClick={() => setActiveTab("generation-mix")}
            className={`px-3 py-1.5 rounded-md text-xs font-mono font-medium transition-all cursor-pointer ${
              activeTab === "generation-mix"
                ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            RENEWABLE MIX
          </button>
        </div>
      </div>

      {/* Chart Canvas Display */}
      <div className="h-[320px] w-full pt-2">
        {activeTab === "load-gen" && (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id="colorGeneration" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="colorLoad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }} />
              <YAxis stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }} unit=" MW" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#090d16",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontFamily: "monospace",
                  color: "#f8fafc",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace", paddingTop: "8px" }} />
              <Area
                type="monotone"
                dataKey="generationMW"
                name="Total Generation (MW)"
                stroke="#f59e0b"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#colorGeneration)"
              />
              <Area
                type="monotone"
                dataKey="loadMW"
                name="Grid Load Demand (MW)"
                stroke="#06b6d4"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorLoad)"
              />
              <Line
                type="monotone"
                dataKey="baselineMW"
                name="24h Baseline Forecast (MW)"
                stroke="#64748b"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {activeTab === "frequency" && (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }} />
              <YAxis
                domain={[49.9, 50.1]}
                stroke="#64748b"
                tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }}
                unit=" Hz"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#090d16",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontFamily: "monospace",
                  color: "#f8fafc",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace", paddingTop: "8px" }} />
              <ReferenceLine y={50.05} stroke="#f43f5e" strokeDasharray="3 3" label={{ value: "Max Overfrequency (+0.05 Hz)", fill: "#f43f5e", fontSize: 10, position: "insideTopRight" }} />
              <ReferenceLine y={50.0} stroke="#10b981" strokeWidth={1} label={{ value: "Nominal 50.00 Hz", fill: "#10b981", fontSize: 10, position: "insideLeft" }} />
              <ReferenceLine y={49.95} stroke="#f43f5e" strokeDasharray="3 3" label={{ value: "Min Underfrequency (-0.05 Hz)", fill: "#f43f5e", fontSize: 10, position: "insideBottomRight" }} />
              <Line
                type="monotone"
                dataKey="frequencyHz"
                name="PMU Frequency (Hz)"
                stroke="#38bdf8"
                strokeWidth={2.5}
                dot={{ fill: "#38bdf8", r: 3 }}
                activeDot={{ r: 6, fill: "#f59e0b" }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}

        {activeTab === "generation-mix" && (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" opacity={0.6} />
              <XAxis dataKey="time" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }} />
              <YAxis stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11, fontFamily: "monospace" }} unit=" MW" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#090d16",
                  borderColor: "#334155",
                  borderRadius: "8px",
                  fontSize: "12px",
                  fontFamily: "monospace",
                  color: "#f8fafc",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px", fontFamily: "monospace", paddingTop: "8px" }} />
              <Bar dataKey="solarMW" name="Solar PV (MW)" stackId="a" fill="#fbbf24" />
              <Bar dataKey="windMW" name="Wind Power (MW)" stackId="a" fill="#06b6d4" />
              <Bar dataKey="bessMW" name="BESS Storage (MW)" stackId="a" fill="#10b981" />
              <Bar dataKey="thermalMW" name="Thermal/Gas Dispatch (MW)" stackId="a" fill="#64748b" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Telemetry Summary Footer */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-800/80 text-xs font-mono">
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 text-[10px] block">PEAK DEMAND TIME</span>
          <span className="text-slate-100 font-bold">{peakPoint.time} ({peakPoint.loadMW.toLocaleString()} MW)</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 text-[10px] block">RENEWABLE PENETRATION</span>
          <span className="text-emerald-400 font-bold">{maxRenewablePercent.toFixed(1)}% Peak</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 text-[10px] block">AVG FREQ DEVIATION</span>
          <span className="text-cyan-400 font-bold">±0.018 Hz</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800">
          <span className="text-slate-500 text-[10px] block">INERTIA CONSTANT (H)</span>
          <span className="text-amber-400 font-bold">4.82 s (Secure)</span>
        </div>
      </div>
    </div>
  );
};
