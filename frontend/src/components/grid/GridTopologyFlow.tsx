"use client";

import React, { useMemo, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  MarkerType,
} from "@xyflow/react";
import {
  SolarNode,
  WindNode,
  SubstationNode,
  BatteryNode,
  CityLoadNode,
} from "./CustomNodes";
import { Activity, Play, RefreshCw, Zap } from "lucide-react";
import { useGridTelemetry } from "@/hooks/useGridTelemetry";

const initialNodes: Node[] = [
  {
    id: "solar-1",
    type: "solar",
    position: { x: 40, y: 30 },
    width: 220,
    height: 115,
    data: {
      label: "Desert Sun Array Alpha",
      type: "solar",
      output: "850 MW",
      capacity: "1,000 MW",
      status: "OPTIMAL",
    },
  },
  {
    id: "wind-1",
    type: "wind",
    position: { x: 40, y: 220 },
    width: 220,
    height: 115,
    data: {
      label: "Highland Wind Farm",
      type: "wind",
      output: "620 MW",
      capacity: "750 MW",
      status: "ONLINE",
    },
  },
  {
    id: "battery-1",
    type: "battery",
    position: { x: 360, y: 330 },
    width: 220,
    height: 115,
    data: {
      label: "NeoStorage BESS 400MWh",
      type: "battery",
      soc: "84.5%",
      status: "OPTIMAL",
    },
  },
  {
    id: "substation-alpha",
    type: "substation",
    position: { x: 360, y: 120 },
    width: 230,
    height: 125,
    data: {
      label: "Hub Substation 400kV",
      type: "substation",
      output: "1,840 MW",
      voltage: "401.2 kV",
      status: "SYNC",
    },
  },
  {
    id: "substation-beta",
    type: "substation",
    position: { x: 690, y: 120 },
    width: 230,
    height: 125,
    data: {
      label: "Metro Step-Down 220kV",
      type: "substation",
      output: "2,420 MW",
      voltage: "220.8 kV",
      status: "SYNC",
    },
  },
  {
    id: "city-load",
    type: "cityLoad",
    position: { x: 1010, y: 120 },
    width: 230,
    height: 125,
    data: {
      label: "Metro Central Load Zone",
      type: "cityLoad",
      load: "2,420 MW",
      status: "OPTIMAL",
    },
  },
];

const initialEdges: Edge[] = [
  {
    id: "e-solar-sub",
    source: "solar-1",
    target: "substation-alpha",
    sourceHandle: "solar-out",
    targetHandle: "sub-left",
    type: "smoothstep",
    animated: true,
    className: "animate-flow-amber",
    style: { stroke: "#f59e0b", strokeWidth: 2.5 },
    label: "850 MW (Solar PV)",
    labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" },
    labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 },
    labelBgPadding: [6, 4],
    markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b", width: 16, height: 16 },
  },
  {
    id: "e-wind-sub",
    source: "wind-1",
    target: "substation-alpha",
    sourceHandle: "wind-out",
    targetHandle: "sub-left",
    type: "smoothstep",
    animated: true,
    className: "animate-flow-cyan",
    style: { stroke: "#06b6d4", strokeWidth: 2.5 },
    label: "620 MW (Wind Feeder)",
    labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" },
    labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 },
    labelBgPadding: [6, 4],
    markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4", width: 16, height: 16 },
  },
  {
    id: "e-bess-sub",
    source: "battery-1",
    target: "substation-alpha",
    sourceHandle: "bess-out",
    targetHandle: "sub-bottom",
    type: "smoothstep",
    animated: true,
    className: "animate-flow-emerald",
    style: { stroke: "#10b981", strokeWidth: 2.5 },
    label: "+180 MW (BESS Discharge)",
    labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" },
    labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 },
    labelBgPadding: [6, 4],
    markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981", width: 16, height: 16 },
  },
  {
    id: "e-sub-sub",
    source: "substation-alpha",
    target: "substation-beta",
    sourceHandle: "sub-right",
    targetHandle: "sub-left",
    type: "smoothstep",
    animated: true,
    className: "animate-flow-blue",
    style: { stroke: "#3b82f6", strokeWidth: 3.5 },
    label: "400kV Bulk Trunk (1,650 MW)",
    labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" },
    labelBgStyle: { fill: "#090d16", stroke: "#3b82f660", strokeWidth: 1, rx: 4, ry: 4 },
    labelBgPadding: [8, 4],
    markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6", width: 18, height: 18 },
  },
  {
    id: "e-sub-city",
    source: "substation-beta",
    target: "city-load",
    sourceHandle: "sub-right",
    targetHandle: "city-in",
    type: "smoothstep",
    animated: true,
    className: "animate-flow-rose",
    style: { stroke: "#f43f5e", strokeWidth: 3.5 },
    label: "Metro Demand: 2,420 MW",
    labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" },
    labelBgStyle: { fill: "#090d16", stroke: "#f43f5e60", strokeWidth: 1, rx: 4, ry: 4 },
    labelBgPadding: [8, 4],
    markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e", width: 18, height: 18 },
  },
];

export const GridTopologyFlow: React.FC = () => {
  const [nodes] = useState<Node[]>(initialNodes);
  const [edges] = useState<Edge[]>(initialEdges);
  const [isSimulating, setIsSimulating] = useState(false);
  const { frequencyHz, isConnected } = useGridTelemetry();

  const nodeTypes = useMemo(
    () => ({
      solar: SolarNode,
      wind: WindNode,
      substation: SubstationNode,
      battery: BatteryNode,
      cityLoad: CityLoadNode,
    }),
    []
  );

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-950/90 shadow-2xl overflow-hidden backdrop-blur-xl">
      {/* Topology Header & Control Toolbar */}
      <div className="p-4 bg-slate-900/80 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
            <Zap className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-slate-100 font-mono tracking-tight">
                LIVE GRID TOPOLOGY TWIN
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                DYNAMIC AC POWER FLOW
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Interactive IEEE multi-bus digital twin representation with active telemetry power vectors.
            </p>
          </div>
        </div>

        {/* Live Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            <Activity className={`w-3.5 h-3.5 ${isConnected ? "text-emerald-400 animate-pulse" : "text-slate-500"}`} />
            <span>FLOW RATE: {frequencyHz !== null ? `${frequencyHz.toFixed(2)} Hz` : "50.00 Hz"}</span>
          </div>

          <button
            onClick={() => setIsSimulating(!isSimulating)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
              isSimulating
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : "bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30"
            }`}
          >
            {isSimulating ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                CONTINGENCY RUNNING
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                SIMULATE N-1 TRIP
              </>
            )}
          </button>
        </div>
      </div>

      {/* React Flow Canvas Container */}
      <div className="h-[500px] w-full relative bg-tech-grid">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.15 }}
          minZoom={0.4}
          maxZoom={1.6}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1e293b" gap={24} size={1.2} />
          
          {/* Controls placed top-right so they don't conflict with MiniMap or Legend */}
          <Controls position="top-right" showInteractive={false} />
          
          {/* Functional, styled MiniMap at bottom-right */}
          <MiniMap
            position="bottom-right"
            nodeColor={(n) => {
              if (n.type === "solar") return "#f59e0b";
              if (n.type === "wind") return "#06b6d4";
              if (n.type === "battery") return "#10b981";
              if (n.type === "cityLoad") return "#f43f5e";
              return "#3b82f6";
            }}
            nodeStrokeColor={(n) => {
              if (n.type === "solar") return "#fbbf24";
              if (n.type === "wind") return "#38bdf8";
              if (n.type === "battery") return "#34d399";
              if (n.type === "cityLoad") return "#fb7185";
              return "#60a5fa";
            }}
            nodeStrokeWidth={2}
            nodeBorderRadius={4}
            maskColor="rgba(7, 9, 14, 0.75)"
            maskStrokeColor="#f59e0b"
            maskStrokeWidth={1.5}
            zoomable
            pannable
            style={{
              width: 170,
              height: 110,
              backgroundColor: "#090d16",
              border: "1px solid rgba(255, 255, 255, 0.12)",
              borderRadius: "8px",
              margin: 12,
            }}
          />
        </ReactFlow>

        {/* Legend Overlay at bottom left */}
        <div className="absolute bottom-3 left-3 z-10 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-lg p-2.5 shadow-xl text-[11px] font-mono text-slate-300 space-y-1 hidden md:block">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">POWER VECTORS</div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
            <span>Solar Generation (PV)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span>Wind Kinetic Feeder</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span>BESS Storage (+180 MW)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span>
            <span>400kV Bulk Transmission</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>Metro Load Sink (2,420 MW)</span>
          </div>
        </div>
      </div>
    </div>
  );
};
