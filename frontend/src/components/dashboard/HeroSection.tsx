"use client";

import { Play, Sliders, Terminal } from "lucide-react";

interface HeroSectionProps {
  onRunSimulation?: () => void;
  onWhatIfScenario?: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
  onRunSimulation,
  onWhatIfScenario,
}) => {
  return (
    <div className="relative rounded-2xl border border-slate-800 bg-gradient-to-b from-slate-900/90 to-slate-950/90 p-6 sm:p-8 backdrop-blur-xl shadow-2xl overflow-hidden">
      {/* Background glow and subtle vector lines */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
        {/* Left text & technical metadata */}
        <div className="space-y-4 max-w-3xl">
          {/* Status Line */}
          <div className="flex flex-wrap items-center gap-2 font-mono text-[11px]">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-500/30 text-emerald-400 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              SYSTEM ONLINE
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              GRID SYNCHRONIZED
            </span>
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-amber-950/60 border border-amber-500/30 text-amber-400 font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              AI ENGINE READY
            </span>
            <span className="text-slate-500 hidden sm:inline">|</span>
            <span className="text-slate-400 hidden sm:inline flex items-center gap-1">
              <Terminal className="w-3 h-3 text-slate-500" />
              IEEE 118-BUS TWIN
            </span>
          </div>

          {/* Heading */}
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-slate-100 font-mono">
              AI-Powered <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-amber-300 to-yellow-500">Grid Intelligence</span>
            </h1>
            <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed font-sans max-w-2xl">
              PULSEiQ is an enterprise-grade electricity grid digital twin platform for real-time SCADA telemetry monitoring, N-1/N-2 contingency risk simulation, generative what-if scenario exploration, and automated dispatch optimization.
            </p>
          </div>
        </div>

        {/* Right CTA Action Buttons */}
        <div className="flex flex-col sm:flex-row lg:flex-col gap-3 shrink-0">
          <button
            onClick={onRunSimulation}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-mono text-sm font-black flex items-center justify-center gap-2 shadow-xl shadow-amber-500/20 hover:shadow-amber-500/30 transition-all cursor-pointer transform hover:-translate-y-0.5"
          >
            <Play className="w-4 h-4 fill-slate-950" />
            <span>RUN CONTINGENCY SIMULATION</span>
          </button>

          <button
            onClick={onWhatIfScenario}
            className="px-6 py-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500/50 text-slate-200 hover:text-white font-mono text-sm font-semibold flex items-center justify-center gap-2 shadow-lg transition-all cursor-pointer"
          >
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>WHAT-IF SCENARIO BUILDER</span>
          </button>
        </div>
      </div>
    </div>
  );
};
