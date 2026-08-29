"use client";

import React, { useState } from "react";
import {
  Zap,
  Bell,
  Sliders,
  Play,
  Cpu,
  ShieldAlert,
  BarChart3,
  Network,
  Settings,
  Radio,
} from "lucide-react";
import { useGridTelemetry } from "@/hooks/useGridTelemetry";

interface NavbarProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  onRunSimulation?: () => void;
  onWhatIfScenario?: () => void;
  frequencyHz?: number | null;
  isConnected?: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab = "dashboard",
  onTabChange,
  onRunSimulation,
  onWhatIfScenario,
  frequencyHz: propFrequencyHz,
  isConnected: propIsConnected,
}) => {
  const [activeNav, setActiveNav] = useState(activeTab);
  
  // Use internal hook if props are not explicitly provided
  const internalTelemetry = useGridTelemetry();
  const isConnected = propIsConnected !== undefined ? propIsConnected : internalTelemetry.isConnected;
  const frequencyHz = propFrequencyHz !== undefined ? propFrequencyHz : internalTelemetry.frequencyHz;

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "grid-twin", label: "Grid Twin", icon: <Network className="w-4 h-4" /> },
    { id: "simulation", label: "Simulation", icon: <Play className="w-4 h-4" /> },
    { id: "risk-analysis", label: "Risk Analysis", icon: <ShieldAlert className="w-4 h-4" /> },
    { id: "ai-forecast", label: "AI Forecast", icon: <Cpu className="w-4 h-4" /> },
  ];

  const handleNavClick = (id: string) => {
    setActiveNav(id);
    if (onTabChange) onTabChange(id);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 shadow-2xl">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & System Status Tag */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/40 text-amber-400 shadow-lg shadow-amber-500/10 group-hover:border-amber-400 transition-all">
                <Zap className="w-5 h-5 fill-amber-400/20" />
                <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                </span>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-black tracking-wider text-slate-100 font-mono">
                    PULSE<span className="text-amber-400">iQ</span>
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-slate-900 text-slate-400 border border-slate-700/60">
                    v0.2.0 • TWIN
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 tracking-tight hidden sm:inline-block">
                  ELECTRICITY GRID RISK SIMULATION & OPTIMIZATION
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden lg:flex items-center gap-1 ml-6 pl-6 border-l border-slate-800">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${
                    activeNav === item.id
                      ? "bg-slate-900 text-amber-400 border border-amber-500/30 shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                  }`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>
          </div>

          {/* Right Side: Telemetry, Action Buttons, Alerts, User */}
          <div className="flex items-center gap-3">
            {/* Grid Online / Offline Real-time Telemetry Pill */}
            {isConnected ? (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-[11px] font-mono text-emerald-400">
                <Radio className="w-3.5 h-3.5 animate-pulse" />
                <span className="font-bold">GRID ONLINE</span>
                <span className="text-slate-500">|</span>
                <span>{frequencyHz !== null && frequencyHz !== undefined ? `${frequencyHz.toFixed(2)} Hz` : "50.00 Hz"}</span>
              </div>
            ) : (
              <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-950/40 border border-rose-500/30 text-[11px] font-mono text-rose-400">
                <Radio className="w-3.5 h-3.5 text-rose-500" />
                <span className="font-bold">GRID OFFLINE</span>
                <span className="text-slate-500">|</span>
                <span>RECONNECTING...</span>
              </div>
            )}

            {/* Action Buttons */}
            <div className="hidden md:flex items-center gap-2">
              <button
                onClick={onWhatIfScenario}
                className="px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-700 text-xs font-mono font-medium text-slate-200 hover:text-white flex items-center gap-1.5 transition-all cursor-pointer"
                title="Configure What-If Scenario Sandbox"
              >
                <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                <span>WHAT-IF</span>
              </button>

              <button
                onClick={onRunSimulation}
                className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-mono text-xs font-bold flex items-center gap-1.5 shadow-lg shadow-amber-500/20 transition-all cursor-pointer"
                title="Execute Grid N-1 Contingency Simulation"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>SIMULATE</span>
              </button>
            </div>

            {/* Alerts Indicator */}
            <button
              className="relative p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
              title="System Alerts: 1 Advisory"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-slate-950 text-[9px] font-mono font-bold">
                1
              </span>
            </button>

            {/* Profile / Settings */}
            <div className="flex items-center gap-1.5 pl-2 border-l border-slate-800">
              <button
                className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
                title="Control Room Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-700 flex items-center justify-center text-slate-300 font-mono text-xs font-bold">
                OP1
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
