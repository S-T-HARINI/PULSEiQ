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
  frequencyHz?: number;
  wsStatus?: "connected" | "connecting" | "disconnected" | "error";
  alertsCount?: number;
  backendOnline?: boolean;
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
  onTabChange,
  onRunSimulation,
  onWhatIfScenario,
}) => {
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
    if (wsStatus === "connected") return "GRID ONLINE";
    if (wsStatus === "connecting") return "SYNCHRONIZING";
    return "STANDBY";
  };

  const getStatusColor = () => {
    if (!backendOnline || wsStatus === "error") {
      return "bg-rose-950/40 border-rose-500/30 text-rose-400";
    }
    if (wsStatus === "connected") {
      return "bg-emerald-950/40 border-emerald-500/30 text-emerald-400";
    }
    return "bg-amber-950/40 border-amber-500/30 text-amber-400";
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-slate-950/95 backdrop-blur-md border-b border-slate-800/80 shadow-2xl">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand & System Status Tag */}
          <div className="flex items-center gap-4">
            <div 
              onClick={() => handleNavClick("dashboard")}
              className="flex items-center gap-3 group cursor-pointer"
            >
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
              {navItems.map((item) => {
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => handleNavClick(item.id)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all cursor-pointer ${
                      isActive
                        ? "bg-slate-900 text-amber-400 border border-amber-500/40 shadow-md shadow-amber-500/10 font-bold"
                        : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                    }`}
                  >
                    {item.icon}
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Right Side: Telemetry, Action Buttons, Alerts, User */}
          <div className="flex items-center gap-3">
            {/* Grid Online Telemetry Pill */}
            <div className={`hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full border text-[11px] font-mono ${getStatusColor()}`}>
              <Radio className="w-3.5 h-3.5 animate-pulse" />
              <span className="font-bold">{getStatusText()}</span>
              <span className="text-slate-500">|</span>
              <span>{frequencyHz.toFixed(2)} Hz</span>
            </div>

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
              title={`System Alerts: ${alertsCount} Active`}
            >
              <Bell className="w-4 h-4" />
              {alertsCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-amber-500 text-slate-950 text-[9px] font-mono font-bold">
                  {alertsCount}
                </span>
              )}
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

        {/* Mobile Navigation Strip */}
        <div className="lg:hidden flex items-center gap-2 overflow-x-auto py-2 border-t border-slate-850">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-mono whitespace-nowrap ${
                  isActive
                    ? "bg-slate-900 text-amber-400 border border-amber-500/40 font-bold"
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
