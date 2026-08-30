"use client";

import React from "react";
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

interface NavbarProps {
  activeTab?: string;
  frequencyHz?: number | null;
  wsStatus?: "connected" | "connecting" | "disconnected" | "error";
  alertsCount?: number;
  backendOnline?: boolean;
  isConnected?: boolean;
  onTabChange?: (tab: string) => void;
  onRunSimulation?: () => void;
  onWhatIfScenario?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab = "dashboard",
  frequencyHz = 50.02,
  wsStatus = "connected",
  alertsCount = 0,
  backendOnline = true,
  isConnected,
  onTabChange,
  onRunSimulation,
  onWhatIfScenario,
}) => {
  const isOnline = isConnected !== undefined ? isConnected : wsStatus === "connected";

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "grid-twin", label: "Grid Twin", icon: <Network className="w-4 h-4" /> },
    { id: "simulation", label: "Simulation", icon: <Play className="w-4 h-4" /> },
    { id: "risk-analysis", label: "Risk Analysis", icon: <ShieldAlert className="w-4 h-4" /> },
    { id: "ai-forecast", label: "AI Forecast", icon: <Cpu className="w-4 h-4" /> },
  ];

  const handleNavClick = (id: string) => {
    if (onTabChange) onTabChange(id);
  };

  const getStatusText = () => {
    if (!backendOnline) return "BACKEND OFFLINE";
    if (isOnline) return "GRID ONLINE";
    if (wsStatus === "connecting") return "SYNCHRONIZING";
    return "STANDBY";
  };

  const getStatusColor = () => {
    if (!backendOnline || wsStatus === "error") {
      return "bg-rose-950/40 border-rose-500/30 text-rose-400";
    }
    if (isOnline) {
      return "bg-emerald-950/40 border-emerald-500/30 text-emerald-400";
    }
    return "bg-amber-950/40 border-amber-500/30 text-amber-400";
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-[#070a12]/90 backdrop-blur-xl border-b border-slate-800/80 shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
      <div className="max-w-[1680px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & System Status Tag */}
          <div className="flex items-center gap-4">
            <div 
              onClick={() => handleNavClick("dashboard")}
              className="flex items-center gap-3 group cursor-pointer select-none"
            >
              <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500/20 to-amber-500/5 border border-amber-500/40 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.2)] group-hover:border-amber-400 group-hover:shadow-[0_0_20px_rgba(245,158,11,0.35)] transition-all">
                <Zap className="w-5 h-5 fill-amber-400/30" />
                <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-amber-500"></span>
                </span>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-lg font-black tracking-wider text-slate-100 font-mono">
                    PULSE<span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-yellow-400">iQ</span>
                  </span>
                  <span className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-slate-900/90 text-amber-400/90 border border-amber-500/30 shadow-xs">
                    v0.2.0 • AI-CORE
                  </span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 tracking-tight hidden sm:inline-block">
                  NEXT-GEN ELECTRICITY GRID DIGITAL TWIN
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="hidden lg:flex items-center gap-1.5 ml-6 pl-6 border-l border-slate-800/80">
              {navItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-mono font-medium transition-all duration-150 cursor-pointer ${
                      isActive
                        ? "bg-slate-900/90 text-amber-300 border border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.15)] font-bold"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60 border border-transparent"
                    }`}
                  >
                    <span className={isActive ? "text-amber-400" : "text-slate-500"}>
                      {item.icon}
                    </span>
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Side: Telemetry, Action Buttons, Alerts, User */}
          <div className="flex items-center gap-3">
            {/* Grid Online Telemetry Pill */}
            <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border text-[11px] font-mono shadow-xs backdrop-blur-md ${getStatusColor()}`}>
              <Radio className={`w-3.5 h-3.5 ${isOnline ? "animate-pulse" : ""}`} />
              <span className="font-bold tracking-tight">{getStatusText()}</span>
              <span className="text-slate-600">|</span>
              <span className="font-semibold">{frequencyHz !== null && frequencyHz !== undefined ? `${frequencyHz.toFixed(2)} Hz` : "50.00 Hz"}</span>
            </div>

            {/* Action Buttons */}
            <div className="hidden md:flex items-center gap-2">
              <button
                onClick={onWhatIfScenario}
                className="px-3.5 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-850 border border-slate-700/80 hover:border-cyan-500/40 text-xs font-mono font-medium text-slate-200 hover:text-cyan-300 flex items-center gap-1.5 transition-all shadow-xs hover:shadow-[0_0_12px_rgba(6,182,212,0.15)] cursor-pointer"
                title="Configure What-If Scenario Sandbox"
              >
                <Sliders className="w-3.5 h-3.5 text-cyan-400" />
                <span>WHAT-IF</span>
              </button>

              <button
                onClick={onRunSimulation}
                className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-mono text-xs font-black flex items-center gap-1.5 shadow-[0_0_18px_rgba(245,158,11,0.3)] hover:shadow-[0_0_24px_rgba(245,158,11,0.45)] transition-all cursor-pointer transform hover:-translate-y-0.5"
                title="Execute Grid N-1 Contingency Simulation"
              >
                <Play className="w-3.5 h-3.5 fill-slate-950" />
                <span>SIMULATE</span>
              </button>
            </div>

            {/* Alerts Indicator */}
            <button
              className="relative p-2 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-all cursor-pointer"
              title={`System Alerts: ${alertsCount} Active`}
            >
              <Bell className="w-4 h-4" />
              {alertsCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-slate-950 text-[9px] font-mono font-bold shadow-xs">
                  {alertsCount}
                </span>
              )}
            </button>

            {/* Profile / Settings */}
            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <button
                className="p-2 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer"
                title="Control Room Settings"
              >
                <Settings className="w-4 h-4" />
              </button>
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-slate-800 to-slate-700 border border-slate-600/60 flex items-center justify-center text-amber-300 font-mono text-xs font-bold shadow-inner">
                OP1
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Navigation Strip */}
        <div className="lg:hidden flex items-center gap-2 overflow-x-auto py-2.5 border-t border-slate-800/80">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-mono whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-slate-900 text-amber-300 border border-amber-500/50 font-bold shadow-xs"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
