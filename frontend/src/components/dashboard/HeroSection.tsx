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
    <div className="relative rounded-2xl border border-slate-800/90 bg-gradient-to-b from-[#0c101a] via-[#090d16] to-[#07090e] p-6 sm:p-8 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.6)] overflow-hidden">
      {/* Background glow and subtle vector lines */}
      <div className="absolute top-0 right-0 w-[450px] h-[450px] bg-amber-500/5 rounded-full blur-3xl pointer-events-none -mr-28 -mt-28"></div>
      <div className="absolute bottom-0 left-1/4 w-[380px] h-[380px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>

      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
        {/* Left text & technical metadata */}
        <div className="space-y-4 max-w-3xl">
          {/* Status Line */}
          <div className="flex flex-wrap items-center gap-2 font-mono text-[11px]">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/70 border border-emerald-500/40 text-emerald-400 font-semibold shadow-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              SYSTEM ONLINE
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-500/40 text-cyan-400 font-semibold shadow-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
              GRID SYNCHRONIZED
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-950/70 border border-amber-500/40 text-amber-400 font-semibold shadow-xs">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
              AI ENGINE READY
            </span>
            <span className="text-slate-700 hidden sm:inline">|</span>
            <span className="text-slate-400 hidden sm:inline-flex items-center gap-1.5 font-mono text-[11px]">
              <Terminal className="w-3.5 h-3.5 text-amber-400" />
              IEEE 50-NODE MESHED TWIN
            </span>
          </div>

          {/* Heading */}
          <div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-slate-100 font-mono">
              AI-Powered <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-yellow-300 to-amber-500">Grid Intelligence</span>
            </h1>
            <p className="mt-3 text-sm sm:text-base text-slate-300 leading-relaxed font-sans max-w-2xl font-normal">
              PULSEiQ is an enterprise-grade digital twin platform for real-time SCADA telemetry monitoring, N-1/N-2 contingency risk simulation, generative what-if scenario exploration, and automated dispatch optimization.
            </p>
          </div>
        </div>

        {/* Right CTA Action Buttons */}
        <div className="flex flex-col sm:flex-row lg:flex-col gap-3.5 shrink-0">
          <button
            onClick={onRunSimulation}
            className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-mono text-xs sm:text-sm font-black flex items-center justify-center gap-2.5 shadow-[0_0_25px_rgba(245,158,11,0.3)] hover:shadow-[0_0_35px_rgba(245,158,11,0.5)] transition-all cursor-pointer transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <Play className="w-4 h-4 fill-slate-950" />
            <span>RUN CONTINGENCY SIMULATION</span>
          </button>

          <button
            onClick={onWhatIfScenario}
            className="px-6 py-3.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700/80 hover:border-cyan-500/50 text-slate-200 hover:text-white font-mono text-xs sm:text-sm font-semibold flex items-center justify-center gap-2.5 shadow-lg hover:shadow-[0_0_20px_rgba(6,182,212,0.2)] transition-all cursor-pointer transform hover:-translate-y-0.5 active:translate-y-0"
          >
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>WHAT-IF SCENARIO BUILDER</span>
          </button>
        </div>
      </div>
    </div>
  );
};
