"use client";

import React from "react";
import {
  CustomGridSummary,
} from "@/types/api";
import {
  Plus,
  Network,
  Trash2,
  Edit3,
  CheckCircle2,
  Zap,
  Layers,
  Sparkles,
} from "lucide-react";

interface CustomGridListProps {
  grids: CustomGridSummary[];
  loading: boolean;
  activeGridId?: string;
  onCreateNew: () => void;
  onEditGrid: (gridId: string) => void;
  onActivateGrid: (gridId: string) => void;
  onDeleteGrid: (gridId: string) => void;
  isActivatingId?: string | null;
  isDeletingId?: string | null;
}

export const CustomGridList: React.FC<CustomGridListProps> = ({
  grids,
  loading,
  activeGridId = "reference_demo_grid",
  onCreateNew,
  onEditGrid,
  onActivateGrid,
  onDeleteGrid,
  isActivatingId,
  isDeletingId,
}) => {
  const customGrids = grids.filter((g) => !g.is_reference);

  return (
    <div className="space-y-6">
      {/* Top Banner with Action Controls */}
      <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-6 backdrop-blur-2xl shadow-[0_20px_50px_rgba(0,0,0,0.6)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-black font-mono text-slate-100 uppercase tracking-tight">
              CUSTOM DIGITAL TWIN DIRECTORY
            </h2>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
              {customGrids.length} REGISTERED
            </span>
          </div>
          <p className="text-xs text-slate-400 font-sans mt-1">
            Create, manage, and activate tailored microgrids, islanded systems, and regional transmission networks.
          </p>
        </div>

        <button
          onClick={onCreateNew}
          className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-mono text-xs font-black flex items-center gap-2 shadow-[0_0_20px_rgba(245,158,11,0.25)] hover:shadow-[0_0_25px_rgba(245,158,11,0.4)] transition-all cursor-pointer transform hover:-translate-y-0.5 shrink-0"
        >
          <Plus className="w-4 h-4" />
          <span>NEW DIGITAL TWIN</span>
        </button>
      </div>

      {/* Grid Directory Content */}
      {loading ? (
        <div className="rounded-2xl border border-slate-800/80 bg-[#090d16]/80 p-12 text-center font-mono text-xs text-slate-400 space-y-3">
          <div className="w-8 h-8 mx-auto border-2 border-amber-400 border-t-transparent rounded-full animate-spin" />
          <p>FETCHING CUSTOM DIGITAL TWINS...</p>
        </div>
      ) : customGrids.length === 0 ? (
        /* Empty State */
        <div className="rounded-2xl border border-dashed border-slate-800 bg-[#090d16]/60 p-12 text-center space-y-5 backdrop-blur-xl">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shadow-[0_0_25px_rgba(245,158,11,0.15)]">
            <Network className="w-8 h-8" />
          </div>
          <div className="space-y-1.5 max-w-md mx-auto">
            <h3 className="text-base font-bold font-mono text-slate-200">No Custom Grids Created Yet</h3>
            <p className="text-xs text-slate-400 font-sans">
              Launch the visual Grid Studio to assemble generators, solar arrays, battery storage, and transmission links into a custom digital twin.
            </p>
          </div>
          <button
            onClick={onCreateNew}
            className="px-5 py-2.5 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 text-amber-300 font-mono text-xs font-bold inline-flex items-center gap-2 transition-all cursor-pointer shadow-lg"
          >
            <Sparkles className="w-4 h-4 text-amber-400" />
            <span>OPEN GRID BUILDER</span>
          </button>
        </div>
      ) : (
        /* Grid Cards */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {customGrids.map((grid) => {
            const isActive = grid.grid_id === activeGridId || grid.is_active;
            const isActivating = isActivatingId === grid.grid_id;
            const isDeleting = isDeletingId === grid.grid_id;

            return (
              <div
                key={grid.grid_id}
                className={`group rounded-2xl border p-5 space-y-4 backdrop-blur-2xl transition-all duration-200 ${
                  isActive
                    ? "bg-[#090d16]/95 border-emerald-500/60 shadow-[0_0_30px_rgba(16,185,129,0.15)] ring-1 ring-emerald-500/30"
                    : "bg-[#090d16]/80 border-slate-800/90 hover:border-slate-700 hover:bg-[#090d16]/95 shadow-xl"
                }`}
              >
                {/* Card Header */}
                <div className="flex items-start justify-between gap-3 border-b border-slate-800/80 pb-3.5">
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-bold font-mono text-slate-100 truncate block">
                        {grid.name}
                      </span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-500 truncate">
                      ID: {grid.grid_id}
                    </div>
                  </div>

                  {isActive ? (
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 flex items-center gap-1.5 shrink-0 shadow-xs">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      ACTIVE TWIN
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-full text-[10px] font-mono font-medium bg-slate-900/80 text-slate-400 border border-slate-800 shrink-0">
                      STANDBY
                    </span>
                  )}
                </div>

                {/* Description */}
                <p className="text-xs text-slate-400 font-sans line-clamp-2 min-h-[32px]">
                  {grid.description || "Custom user-defined electricity grid digital twin."}
                </p>

                {/* Metrics Badges */}
                <div className="grid grid-cols-2 gap-2.5 font-mono text-xs">
                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                    <div className="text-[10px] text-slate-500 flex items-center gap-1">
                      <Layers className="w-3 h-3 text-cyan-400" />
                      <span>TOPOLOGY</span>
                    </div>
                    <div className="text-slate-200 font-bold">
                      {grid.node_count} Nodes <span className="text-slate-500 font-normal">/</span> {grid.edge_count} Lines
                    </div>
                  </div>

                  <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800/80 space-y-1">
                    <div className="text-[10px] text-slate-500 flex items-center gap-1">
                      <Zap className="w-3 h-3 text-amber-400" />
                      <span>CAPACITY</span>
                    </div>
                    <div className="text-amber-400 font-bold truncate">
                      {Math.round(grid.total_generation_mw)} MW
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="pt-2 flex items-center justify-between gap-2 border-t border-slate-800/80">
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => onEditGrid(grid.grid_id)}
                      className="px-3 py-1.5 rounded-lg bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white font-mono text-xs flex items-center gap-1.5 transition-all cursor-pointer"
                      title="Open in Visual Grid Builder"
                    >
                      <Edit3 className="w-3.5 h-3.5 text-cyan-400" />
                      <span>EDIT</span>
                    </button>

                    <button
                      onClick={() => onDeleteGrid(grid.grid_id)}
                      disabled={isDeleting}
                      className="p-1.5 rounded-lg bg-slate-900/90 hover:bg-rose-950/50 border border-slate-800 hover:border-rose-500/40 text-slate-400 hover:text-rose-400 transition-all cursor-pointer disabled:opacity-50"
                      title="Delete Custom Grid"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {!isActive && (
                    <button
                      onClick={() => onActivateGrid(grid.grid_id)}
                      disabled={isActivating}
                      className="px-3.5 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer disabled:opacity-50 shadow-xs"
                      title="Activate this grid for all SCADA telemetry & AI pipelines"
                    >
                      {isActivating ? (
                        <div className="w-3.5 h-3.5 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                      )}
                      <span>ACTIVATE</span>
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
