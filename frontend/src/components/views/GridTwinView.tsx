"use client";

import React, { useState, useEffect, useCallback } from "react";
import { GridTopologyFlow } from "@/components/grid/GridTopologyFlow";
import { CustomGridList } from "@/components/grid/CustomGridList";
import { GridStudioBuilder } from "@/components/grid/GridStudioBuilder";
import { Node, Edge } from "@xyflow/react";
import {
  Network,
  Zap,
  Activity,
  ShieldCheck,
  Radio,
  Sliders,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { CustomGridSummary, GridDetailResponse } from "@/types/api";
import { pulseApi } from "@/lib/api";

interface GridTwinViewProps {
  topologyNodes?: Node[];
  topologyEdges?: Edge[];
  frequencyHz: number;
  isSimulating: boolean;
  onSimulate: () => void;
  activeGridId?: string;
  onGridActivated?: () => void;
}

export const GridTwinView: React.FC<GridTwinViewProps> = ({
  topologyNodes,
  topologyEdges,
  frequencyHz,
  isSimulating,
  onSimulate,
  activeGridId = "reference_demo_grid",
  onGridActivated,
}) => {
  // Grid Studio Mode: "reference" | "custom"
  const [studioMode, setStudioMode] = useState<"reference" | "custom">("reference");

  // Custom Grid State
  const [customGrids, setCustomGrids] = useState<CustomGridSummary[]>([]);
  const [loadingGrids, setLoadingGrids] = useState(false);
  const [isBuilderOpen, setIsBuilderOpen] = useState(false);
  const [editingGrid, setEditingGrid] = useState<GridDetailResponse | null>(null);

  // Action status
  const [isActivatingId, setIsActivatingId] = useState<string | null>(null);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);
  const [feedbackType, setFeedbackType] = useState<"success" | "error">("success");

  const isReferenceActive =
    activeGridId === "reference_demo_grid" ||
    activeGridId === "pulseiq-digital-twin" ||
    !activeGridId;

  // Fetch list of custom grids
  const fetchCustomGrids = useCallback(async () => {
    setLoadingGrids(true);
    try {
      const data = await pulseApi.listCustomGrids();
      setCustomGrids(data);
    } catch (err) {
      console.error("Error fetching custom grids:", err);
    } finally {
      setLoadingGrids(false);
    }
  }, []);

  useEffect(() => {
    fetchCustomGrids();
  }, [fetchCustomGrids]);

  // Activate grid
  const handleActivateGrid = async (gridId: string) => {
    setIsActivatingId(gridId);
    setFeedbackMessage(null);
    try {
      await pulseApi.setActiveGrid(gridId);
      setFeedbackType("success");
      setFeedbackMessage(
        gridId === "reference_demo_grid"
          ? "Reference Demonstration Grid is now active across all SCADA & AI telemetry."
          : `Custom Digital Twin (${gridId}) is now active!`
      );
      await fetchCustomGrids();
      if (onGridActivated) {
        onGridActivated();
      }
    } catch (err) {
      setFeedbackType("error");
      setFeedbackMessage((err as Error).message || "Failed to activate grid.");
    } finally {
      setIsActivatingId(null);
      setTimeout(() => setFeedbackMessage(null), 4000);
    }
  };

  // Open visual builder for editing
  const handleEditGrid = async (gridId: string) => {
    try {
      const detail = await pulseApi.getCustomGrid(gridId);
      setEditingGrid(detail);
      setIsBuilderOpen(true);
    } catch (err) {
      setFeedbackType("error");
      setFeedbackMessage((err as Error).message || "Failed to load grid for editing.");
    }
  };

  // Delete custom grid
  const handleDeleteGrid = async (gridId: string) => {
    if (!window.confirm(`Are you sure you want to delete custom grid '${gridId}'?`)) {
      return;
    }
    setIsDeletingId(gridId);
    try {
      await pulseApi.deleteCustomGrid(gridId);
      setFeedbackType("success");
      setFeedbackMessage(`Custom grid '${gridId}' deleted.`);
      await fetchCustomGrids();
      if (activeGridId === gridId && onGridActivated) {
        onGridActivated();
      }
    } catch (err) {
      setFeedbackType("error");
      setFeedbackMessage((err as Error).message || "Failed to delete custom grid.");
    } finally {
      setIsDeletingId(null);
      setTimeout(() => setFeedbackMessage(null), 3000);
    }
  };

  // Callback when builder finishes saving
  const handleBuilderSaved = async (_gridId: string, activated?: boolean) => {
    setIsBuilderOpen(false);
    setEditingGrid(null);
    await fetchCustomGrids();
    if (activated && onGridActivated) {
      onGridActivated();
    }
  };

  return (
    <div className="space-y-6">
      {/* GRID STUDIO MODE SELECTOR HEADER */}
      <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-6 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.6)] flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-2xl bg-amber-500/10 border border-amber-500/30 text-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.2)]">
            <Network className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-black font-mono text-slate-100 uppercase tracking-tight">
                GRID STUDIO & DIGITAL TWIN
              </h1>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/10 text-amber-300 border border-amber-500/30 shadow-xs">
                {studioMode === "reference" ? "REFERENCE MESH" : "CUSTOM BUILDER"}
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-1 max-w-2xl font-normal">
              Switch between the pre-configured Reference demonstration grid and user-created custom digital twins.
            </p>
          </div>
        </div>

        {/* Segmented Mode Switcher & Telemetry Pill */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
          {/* Mode Switch Pills */}
          <div className="flex items-center p-1 rounded-xl bg-slate-900/90 border border-slate-800 shadow-inner">
            <button
              onClick={() => {
                setStudioMode("reference");
                setIsBuilderOpen(false);
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
                studioMode === "reference"
                  ? "bg-amber-500 text-slate-950 shadow-md"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Zap className="w-3.5 h-3.5" />
              <span>REFERENCE GRID</span>
            </button>

            <button
              onClick={() => {
                setStudioMode("custom");
                fetchCustomGrids();
              }}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold transition-all cursor-pointer flex items-center gap-2 ${
                studioMode === "custom"
                  ? "bg-amber-500 text-slate-950 shadow-md"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>CUSTOM GRID</span>
            </button>
          </div>

          {/* Sub-Second PMU Telemetry Pill */}
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-xs font-mono text-emerald-400 shadow-xs">
            <Radio className="w-3.5 h-3.5 animate-pulse" />
            <span>PMU: {frequencyHz.toFixed(2)} Hz</span>
          </div>
        </div>
      </div>

      {/* Feedback Banner (if any) */}
      {feedbackMessage && (
        <div
          className={`rounded-2xl border p-4 text-xs font-mono flex items-center gap-2.5 backdrop-blur-xl transition-all ${
            feedbackType === "success"
              ? "border-emerald-500/40 bg-emerald-950/40 text-emerald-300"
              : "border-rose-500/40 bg-rose-950/40 text-rose-300"
          }`}
        >
          {feedbackType === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          )}
          <span>{feedbackMessage}</span>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 1. REFERENCE GRID MODE */}
      {/* ========================================================================= */}
      {studioMode === "reference" && (
        <div className="space-y-6">
          {/* Reference Grid Sub-Header with Active State Action */}
          <div className="flex items-center justify-between px-2 text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="text-slate-400">DEMONSTRATION TOPOLOGY:</span>
              <span className="text-slate-200 font-bold">50-BUS REGIONAL POWER POOL</span>
            </div>

            {isReferenceActive ? (
              <span className="px-3 py-1 rounded-full text-[11px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5 shadow-xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                ACTIVE IN SIMULATION & AI PIPELINES
              </span>
            ) : (
              <button
                onClick={() => handleActivateGrid("reference_demo_grid")}
                disabled={isActivatingId === "reference_demo_grid"}
                className="px-3.5 py-1.5 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 font-bold flex items-center gap-1.5 cursor-pointer transition-all shadow-xs"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-amber-400" />
                <span>ACTIVATE REFERENCE GRID</span>
              </button>
            )}
          </div>

          {/* React Flow Reference Topology Canvas */}
          <div className="w-full">
            <GridTopologyFlow
              nodes={topologyNodes}
              edges={topologyEdges}
              frequencyHz={frequencyHz}
              isSimulating={isSimulating}
              onSimulate={onSimulate}
            />
          </div>

          {/* Reference Grid Operational Telemetry Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
            <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-5 space-y-2.5 shadow-xl backdrop-blur-2xl">
              <div className="flex items-center justify-between text-slate-300 pb-2.5 border-b border-slate-800/80">
                <span className="flex items-center gap-2 font-bold">
                  <Zap className="w-4 h-4 text-amber-400" />
                  <span>TOTAL CAPACITY & HEADROOM</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 font-bold">
                  ONLINE
                </span>
              </div>
              <div className="flex justify-between pt-1">
                <span className="text-slate-400">Nameplate Capacity:</span>
                <span className="text-slate-100 font-bold">4,850 MW</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Current Active Load:</span>
                <span className="text-cyan-400 font-bold">3,780 MW</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Available Spinning Reserve:</span>
                <span className="text-emerald-400 font-bold">+1,070 MW</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-5 space-y-2.5 shadow-xl backdrop-blur-2xl">
              <div className="flex items-center justify-between text-slate-300 pb-2.5 border-b border-slate-800/80">
                <span className="flex items-center gap-2 font-bold">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  <span>BUSBAR FREQUENCY & VOLTAGE</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] bg-cyan-950/60 text-cyan-400 border border-cyan-500/30 font-bold">
                  NOMINAL
                </span>
              </div>
              <div className="flex justify-between pt-1">
                <span className="text-slate-400">System Frequency:</span>
                <span className="text-slate-100 font-bold">{frequencyHz.toFixed(2)} Hz</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Hub Bus Voltage:</span>
                <span className="text-emerald-400 font-bold">401.2 kV (1.003 pu)</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Metro Bus Voltage:</span>
                <span className="text-emerald-400 font-bold">220.8 kV (1.004 pu)</span>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-5 space-y-2.5 shadow-xl backdrop-blur-2xl">
              <div className="flex items-center justify-between text-slate-300 pb-2.5 border-b border-slate-800/80">
                <span className="flex items-center gap-2 font-bold">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>N-1 RELIABILITY & STABILITY</span>
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] bg-emerald-950/60 text-emerald-400 border border-emerald-500/30 font-bold">
                  STABLE
                </span>
              </div>
              <div className="flex justify-between pt-1">
                <span className="text-slate-400">Grid Stability Index:</span>
                <span className="text-slate-100 font-bold">98.6%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Active Contingencies:</span>
                <span className="text-slate-100 font-bold">0 Outages</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Inertia Constant (H):</span>
                <span className="text-amber-400 font-bold">4.82 s (Secure)</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 2. CUSTOM GRID MODE */}
      {/* ========================================================================= */}
      {studioMode === "custom" && (
        <div>
          {isBuilderOpen ? (
            /* Visual Grid Studio Builder Canvas */
            <GridStudioBuilder
              initialGrid={editingGrid}
              onBack={() => {
                setIsBuilderOpen(false);
                setEditingGrid(null);
              }}
              onSaved={handleBuilderSaved}
            />
          ) : (
            /* Custom Grid Directory List */
            <CustomGridList
              grids={customGrids}
              loading={loadingGrids}
              activeGridId={activeGridId}
              onCreateNew={() => {
                setEditingGrid(null);
                setIsBuilderOpen(true);
              }}
              onEditGrid={handleEditGrid}
              onActivateGrid={handleActivateGrid}
              onDeleteGrid={handleDeleteGrid}
              isActivatingId={isActivatingId}
              isDeletingId={isDeletingId}
            />
          )}
        </div>
      )}
    </div>
  );
};
