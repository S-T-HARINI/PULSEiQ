"use client";

import React, { useMemo, useState, useEffect } from "react";
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
  ThermalNode,
  SubstationNode,
  BatteryNode,
  CityLoadNode,
} from "./CustomNodes";
import { Activity, Play, RefreshCw, Zap, Layers } from "lucide-react";

// ============================================================================
// 50-NODE ENTERPRISE MESHED GRID TOPOLOGY (6 LOGICAL STAGES)
// ============================================================================
const defaultInitialNodes: Node[] = [
  // ================= COLUMN 1: RENEWABLE GENERATION (X: 40) =================
  {
    id: "gen-solar-1",
    type: "solar",
    position: { x: 40, y: 40 },
    width: 215,
    height: 110,
    data: { label: "Helios Solar Alpha", type: "solar", output: "480 MW", capacity: "500 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-solar-2",
    type: "solar",
    position: { x: 40, y: 180 },
    width: 215,
    height: 110,
    data: { label: "Helios Solar Beta", type: "solar", output: "420 MW", capacity: "450 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-solar-3",
    type: "solar",
    position: { x: 40, y: 320 },
    width: 215,
    height: 110,
    data: { label: "Desert Sun PV 1", type: "solar", output: "380 MW", capacity: "400 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-solar-4",
    type: "solar",
    position: { x: 40, y: 460 },
    width: 215,
    height: 110,
    data: { label: "Desert Sun PV 2", type: "solar", output: "340 MW", capacity: "350 MW", status: "ONLINE" },
  },
  {
    id: "gen-wind-1",
    type: "wind",
    position: { x: 40, y: 600 },
    width: 215,
    height: 110,
    data: { label: "Coastal Ridge Wind A", type: "wind", output: "520 MW", capacity: "550 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-wind-2",
    type: "wind",
    position: { x: 40, y: 740 },
    width: 215,
    height: 110,
    data: { label: "Coastal Ridge Wind B", type: "wind", output: "480 MW", capacity: "500 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-wind-3",
    type: "wind",
    position: { x: 40, y: 880 },
    width: 215,
    height: 110,
    data: { label: "Offshore Wind Alpha", type: "wind", output: "580 MW", capacity: "600 MW", status: "OPTIMAL" },
  },
  {
    id: "gen-wind-4",
    type: "wind",
    position: { x: 40, y: 1020 },
    width: 215,
    height: 110,
    data: { label: "Offshore Wind Beta", type: "wind", output: "420 MW", capacity: "450 MW", status: "ONLINE" },
  },

  // ================= COLUMN 2: THERMAL, NUCLEAR & HYDRO (X: 340) =================
  {
    id: "gen-nuclear-1",
    type: "thermal",
    position: { x: 340, y: 40 },
    width: 215,
    height: 110,
    data: { label: "Apex Nuclear Station", type: "thermal", output: "1,100 MW", capacity: "1,200 MW", status: "SYNC" },
  },
  {
    id: "gen-gas-1",
    type: "thermal",
    position: { x: 340, y: 180 },
    width: 215,
    height: 110,
    data: { label: "Metro Gas Combined 1", type: "thermal", output: "650 MW", capacity: "700 MW", status: "ONLINE" },
  },
  {
    id: "gen-gas-2",
    type: "thermal",
    position: { x: 340, y: 320 },
    width: 215,
    height: 110,
    data: { label: "Metro Gas Combined 2", type: "thermal", output: "580 MW", capacity: "600 MW", status: "ONLINE" },
  },
  {
    id: "gen-hydro-1",
    type: "thermal",
    position: { x: 340, y: 460 },
    width: 215,
    height: 110,
    data: { label: "Cascade Hydro Dam", type: "thermal", output: "450 MW", capacity: "500 MW", status: "ONLINE" },
  },
  {
    id: "gen-peaker-1",
    type: "thermal",
    position: { x: 340, y: 600 },
    width: 215,
    height: 110,
    data: { label: "Fast Peaking Turbine A", type: "thermal", output: "280 MW", capacity: "350 MW", status: "STANDBY" },
  },
  {
    id: "gen-peaker-2",
    type: "thermal",
    position: { x: 340, y: 740 },
    width: 215,
    height: 110,
    data: { label: "Fast Peaking Turbine B", type: "thermal", output: "260 MW", capacity: "300 MW", status: "STANDBY" },
  },
  {
    id: "gen-biomass-1",
    type: "thermal",
    position: { x: 340, y: 880 },
    width: 215,
    height: 110,
    data: { label: "Valley Biomass Unit", type: "thermal", output: "140 MW", capacity: "150 MW", status: "ONLINE" },
  },
  {
    id: "gen-geothermal-1",
    type: "thermal",
    position: { x: 340, y: 1020 },
    width: 215,
    height: 110,
    data: { label: "Geothermal Base Plant", type: "thermal", output: "180 MW", capacity: "200 MW", status: "ONLINE" },
  },

  // ================= COLUMN 3: STEP-UP HUBS & BESS STORAGE (X: 640) =================
  {
    id: "sub-solar-stepup-1",
    type: "substation",
    position: { x: 640, y: 40 },
    width: 220,
    height: 110,
    data: { label: "Solar Step-Up Hub 1", type: "substation", output: "900 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-solar-stepup-2",
    type: "substation",
    position: { x: 640, y: 180 },
    width: 220,
    height: 110,
    data: { label: "Solar Step-Up Hub 2", type: "substation", output: "720 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-wind-stepup-1",
    type: "substation",
    position: { x: 640, y: 320 },
    width: 220,
    height: 110,
    data: { label: "Wind Step-Up Hub 1", type: "substation", output: "1,000 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-wind-stepup-2",
    type: "substation",
    position: { x: 640, y: 460 },
    width: 220,
    height: 110,
    data: { label: "Wind Step-Up Hub 2", type: "substation", output: "1,000 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "bat-bess-1",
    type: "battery",
    position: { x: 640, y: 600 },
    width: 215,
    height: 110,
    data: { label: "NeoStorage BESS 400MWh", type: "battery", output: "+180 MW", soc: "88.5%", status: "OPTIMAL" },
  },
  {
    id: "bat-bess-2",
    type: "battery",
    position: { x: 640, y: 740 },
    width: 215,
    height: 110,
    data: { label: "GridReserve BESS 300MWh", type: "battery", output: "+140 MW", soc: "91.2%", status: "OPTIMAL" },
  },
  {
    id: "bat-bess-3",
    type: "battery",
    position: { x: 640, y: 880 },
    width: 215,
    height: 110,
    data: { label: "Apex BESS Fast Buffer", type: "battery", output: "+95 MW", soc: "85.0%", status: "OPTIMAL" },
  },
  {
    id: "bat-bess-4",
    type: "battery",
    position: { x: 640, y: 1020 },
    width: 215,
    height: 110,
    data: { label: "Highland BESS Stabilizer", type: "battery", output: "+75 MW", soc: "89.0%", status: "OPTIMAL" },
  },

  // ================= COLUMN 4: 400kV BULK TRANSMISSION HUBS & RING (X: 960) =================
  {
    id: "sub-bulk-alpha",
    type: "substation",
    position: { x: 960, y: 40 },
    width: 220,
    height: 110,
    data: { label: "Bulk Substation Alpha 400kV", type: "substation", output: "2,100 MW", voltage: "401.8 kV", status: "SYNC" },
  },
  {
    id: "sub-bulk-beta",
    type: "substation",
    position: { x: 960, y: 150 },
    width: 220,
    height: 110,
    data: { label: "Bulk Substation Beta 400kV", type: "substation", output: "1,950 MW", voltage: "400.9 kV", status: "SYNC" },
  },
  {
    id: "sub-bulk-gamma",
    type: "substation",
    position: { x: 960, y: 260 },
    width: 220,
    height: 110,
    data: { label: "Central Intertie Hub 400kV", type: "substation", output: "2,450 MW", voltage: "402.4 kV", status: "SYNC" },
  },
  {
    id: "sub-bulk-delta",
    type: "substation",
    position: { x: 960, y: 370 },
    width: 220,
    height: 110,
    data: { label: "South Bulk Hub 400kV", type: "substation", output: "1,820 MW", voltage: "399.8 kV", status: "SYNC" },
  },
  {
    id: "sub-bulk-epsilon",
    type: "substation",
    position: { x: 960, y: 480 },
    width: 220,
    height: 110,
    data: { label: "Regional Ring Hub 400kV", type: "substation", output: "1,780 MW", voltage: "400.2 kV", status: "SYNC" },
  },
  {
    id: "sub-bulk-zeta",
    type: "substation",
    position: { x: 960, y: 590 },
    width: 220,
    height: 110,
    data: { label: "North Bulk Switching 400kV", type: "substation", output: "1,550 MW", voltage: "401.1 kV", status: "SYNC" },
  },
  {
    id: "sub-intertie-east",
    type: "substation",
    position: { x: 960, y: 700 },
    width: 220,
    height: 110,
    data: { label: "East Grid Intertie 400kV", type: "substation", output: "1,350 MW", voltage: "401.5 kV", status: "SYNC" },
  },
  {
    id: "sub-intertie-west",
    type: "substation",
    position: { x: 960, y: 810 },
    width: 220,
    height: 110,
    data: { label: "West Grid Intertie 400kV", type: "substation", output: "1,420 MW", voltage: "402.0 kV", status: "SYNC" },
  },
  {
    id: "sub-crossborder",
    type: "substation",
    position: { x: 960, y: 920 },
    width: 220,
    height: 110,
    data: { label: "Cross-Border Tie 400kV", type: "substation", output: "1,250 MW", voltage: "400.6 kV", status: "SYNC" },
  },
  {
    id: "sub-ring-master",
    type: "substation",
    position: { x: 960, y: 1030 },
    width: 220,
    height: 110,
    data: { label: "Central Ring Master 400kV", type: "substation", output: "2,200 MW", voltage: "402.2 kV", status: "SYNC" },
  },

  // ================= COLUMN 5: 220kV / 132kV DISTRIBUTION (X: 1280) =================
  {
    id: "sub-dist-metro-1",
    type: "substation",
    position: { x: 1280, y: 40 },
    width: 220,
    height: 110,
    data: { label: "Metro Step-Down 220kV A", type: "substation", output: "1,480 MW", voltage: "220.5 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-metro-2",
    type: "substation",
    position: { x: 1280, y: 180 },
    width: 220,
    height: 110,
    data: { label: "Metro Step-Down 220kV B", type: "substation", output: "1,050 MW", voltage: "220.0 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-urban-n",
    type: "substation",
    position: { x: 1280, y: 320 },
    width: 220,
    height: 110,
    data: { label: "North Urban Feeder 132kV", type: "substation", output: "980 MW", voltage: "132.2 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-urban-s",
    type: "substation",
    position: { x: 1280, y: 460 },
    width: 220,
    height: 110,
    data: { label: "South Suburban Feeder 132kV", type: "substation", output: "890 MW", voltage: "132.0 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-ind-1",
    type: "substation",
    position: { x: 1280, y: 600 },
    width: 220,
    height: 110,
    data: { label: "Heavy Industrial Sub 220kV", type: "substation", output: "1,120 MW", voltage: "220.1 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-tech",
    type: "substation",
    position: { x: 1280, y: 740 },
    width: 220,
    height: 110,
    data: { label: "Tech Corridor Sub 132kV", type: "substation", output: "760 MW", voltage: "132.4 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-harbor",
    type: "substation",
    position: { x: 1280, y: 880 },
    width: 220,
    height: 110,
    data: { label: "Harbor Logistics Sub 132kV", type: "substation", output: "840 MW", voltage: "132.1 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-airport",
    type: "substation",
    position: { x: 1280, y: 1020 },
    width: 220,
    height: 110,
    data: { label: "Transit & Airport Sub 132kV", type: "substation", output: "720 MW", voltage: "132.5 kV", status: "SYNC" },
  },

  // ================= COLUMN 6: URBAN LOAD SINKS & CRITICAL FACILITIES (X: 1600) =================
  {
    id: "load-hospital-metro",
    type: "cityLoad",
    position: { x: 1600, y: 40 },
    width: 215,
    height: 110,
    data: { label: "Metro University Trauma Hospital", type: "cityLoad", load: "85 MW", status: "OPTIMAL" },
  },
  {
    id: "load-hospital-north",
    type: "cityLoad",
    position: { x: 1600, y: 180 },
    width: 215,
    height: 110,
    data: { label: "North Regional General Hospital", type: "cityLoad", load: "65 MW", status: "OPTIMAL" },
  },
  {
    id: "load-datacenter-cloud",
    type: "cityLoad",
    position: { x: 1600, y: 320 },
    width: 215,
    height: 110,
    data: { label: "Financial Cloud Data Center", type: "cityLoad", load: "340 MW", status: "OPTIMAL" },
  },
  {
    id: "load-ai-supercluster",
    type: "cityLoad",
    position: { x: 1600, y: 460 },
    width: 215,
    height: 110,
    data: { label: "AI GPU Training Supercluster", type: "cityLoad", load: "420 MW", status: "OPTIMAL" },
  },
  {
    id: "load-city-cbd",
    type: "cityLoad",
    position: { x: 1600, y: 600 },
    width: 215,
    height: 110,
    data: { label: "Metro Central CBD", type: "cityLoad", load: "1,140 MW", status: "OPTIMAL" },
  },
  {
    id: "load-industrial-heavy",
    type: "cityLoad",
    position: { x: 1600, y: 740 },
    width: 215,
    height: 110,
    data: { label: "Heavy Manufacturing Park", type: "cityLoad", load: "780 MW", status: "OPTIMAL" },
  },
  {
    id: "load-residential-metro",
    type: "cityLoad",
    position: { x: 1600, y: 880 },
    width: 215,
    height: 110,
    data: { label: "Metro Heights Residential", type: "cityLoad", load: "520 MW", status: "OPTIMAL" },
  },
  {
    id: "load-transit-rail",
    type: "cityLoad",
    position: { x: 1600, y: 1020 },
    width: 215,
    height: 110,
    data: { label: "High-Speed Rail & Port Terminal", type: "cityLoad", load: "390 MW", status: "OPTIMAL" },
  },
];

// ============================================================================
// 80+ INTERCONNECTED HIGH-FIDELITY TRANSMISSION FLOW LINES
// ============================================================================
const defaultInitialEdges: Edge[] = [
  // --- Col 1 (Solar & Wind) -> Col 3 (Step-Up Transformers) ---
  { id: "e-s1-su1", source: "gen-solar-1", target: "sub-solar-stepup-1", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2.5 }, label: "480 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s2-su1", source: "gen-solar-2", target: "sub-solar-stepup-1", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2.5 }, label: "420 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s3-su2", source: "gen-solar-3", target: "sub-solar-stepup-2", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2.5 }, label: "380 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s4-su2", source: "gen-solar-4", target: "sub-solar-stepup-2", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2.5 }, label: "340 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-w1-wu1", source: "gen-wind-1", target: "sub-wind-stepup-1", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "520 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w2-wu1", source: "gen-wind-2", target: "sub-wind-stepup-1", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "480 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w3-wu2", source: "gen-wind-3", target: "sub-wind-stepup-2", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 3 }, label: "580 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w4-wu2", source: "gen-wind-4", target: "sub-wind-stepup-2", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "420 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },

  // --- Col 1 cross-ties to thermal units ---
  { id: "e-s2-th1", source: "gen-solar-2", target: "gen-gas-1", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "120 MW Tie", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-w2-th2", source: "gen-wind-2", target: "gen-hydro-1", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2 }, label: "150 MW Tie", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },

  // --- Col 2 (Thermal / Nuclear / Hydro) -> Col 4 (400kV Bulk Hubs) ---
  { id: "e-nuc-alpha", source: "gen-nuclear-1", target: "sub-bulk-alpha", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 3.5 }, label: "1,100 MW (Nuclear)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-gas1-beta", source: "gen-gas-1", target: "sub-bulk-beta", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 3 }, label: "650 MW (CCGT)", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-gas2-gamma", source: "gen-gas-2", target: "sub-bulk-gamma", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 3 }, label: "580 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-hydro-delta", source: "gen-hydro-1", target: "sub-bulk-delta", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "450 MW (Hydro)", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-peak1-eps", source: "gen-peaker-1", target: "sub-bulk-epsilon", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 2 }, label: "280 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-peak2-zeta", source: "gen-peaker-2", target: "sub-bulk-zeta", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 2 }, label: "260 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-bio-east", source: "gen-biomass-1", target: "sub-intertie-east", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "140 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-geo-west", source: "gen-geothermal-1", target: "sub-intertie-west", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "180 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  // --- Col 3 (Step-Up & BESS) -> Col 4 (400kV Bulk Hubs) ---
  { id: "e-su1-ba", source: "sub-solar-stepup-1", target: "sub-bulk-alpha", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "900 MW (400kV)", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-su2-bb", source: "sub-solar-stepup-2", target: "sub-bulk-beta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "720 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-wu1-bg", source: "sub-wind-stepup-1", target: "sub-bulk-gamma", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,000 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-wu2-bd", source: "sub-wind-stepup-2", target: "sub-bulk-delta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,000 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-b1-be", source: "bat-bess-1", target: "sub-bulk-epsilon", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2.5 }, label: "+180 MW (BESS)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b2-bz", source: "bat-bess-2", target: "sub-bulk-zeta", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2.5 }, label: "+140 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b3-ie", source: "bat-bess-3", target: "sub-intertie-east", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+95 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b4-iw", source: "bat-bess-4", target: "sub-intertie-west", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+75 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  // --- 400kV Bulk Inter-Hub Meshed Ring Network (Loops & Redundancies) ---
  { id: "e-ba-bb", source: "sub-bulk-alpha", target: "sub-bulk-beta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "850 MW Ring", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bb-bg", source: "sub-bulk-beta", target: "sub-bulk-gamma", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "920 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bg-bd", source: "sub-bulk-gamma", target: "sub-bulk-delta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,140 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bd-be", source: "sub-bulk-delta", target: "sub-bulk-epsilon", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "980 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-be-bz", source: "sub-bulk-epsilon", target: "sub-bulk-zeta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "840 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bz-ie", source: "sub-bulk-zeta", target: "sub-intertie-east", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "790 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-ie-iw", source: "sub-intertie-east", target: "sub-intertie-west", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "860 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-iw-cb", source: "sub-intertie-west", target: "sub-crossborder", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "720 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-cb-rm", source: "sub-crossborder", target: "sub-ring-master", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "950 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-rm-ba", source: "sub-ring-master", target: "sub-bulk-alpha", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,180 MW (Ring Master)", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },

  // --- Diagonal Cross-Ties for N-1 Robustness ---
  { id: "e-ba-bg", source: "sub-bulk-alpha", target: "sub-bulk-gamma", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 2.5 }, label: "680 MW Trunk", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bb-bd", source: "sub-bulk-beta", target: "sub-bulk-delta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 2.5 }, label: "640 MW Trunk", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bg-be", source: "sub-bulk-gamma", target: "sub-bulk-epsilon", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 2.5 }, label: "720 MW Trunk", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-bd-bz", source: "sub-bulk-delta", target: "sub-bulk-zeta", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 2.5 }, label: "590 MW Trunk", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },

  // --- Col 4 (400kV Bulk) -> Col 5 (Distribution Substations 220kV/132kV) ---
  { id: "e-ba-d1", source: "sub-bulk-alpha", target: "sub-dist-metro-1", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 3 }, label: "1,480 MW (220kV)", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-bb-d2", source: "sub-bulk-beta", target: "sub-dist-metro-2", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "1,050 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-bg-dn", source: "sub-bulk-gamma", target: "sub-dist-urban-n", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "980 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-bd-ds", source: "sub-bulk-delta", target: "sub-dist-urban-s", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "890 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-be-di", source: "sub-bulk-epsilon", target: "sub-dist-ind-1", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 3 }, label: "1,120 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-bz-dt", source: "sub-bulk-zeta", target: "sub-dist-tech", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "760 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-ie-dh", source: "sub-intertie-east", target: "sub-dist-harbor", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "840 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-iw-da", source: "sub-intertie-west", target: "sub-dist-airport", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "720 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },

  // --- Distribution Ring Cross-Ties (Inter-substation loops) ---
  { id: "e-d1-d2", source: "sub-dist-metro-1", target: "sub-dist-metro-2", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2 }, label: "280 MW Tie", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-dn-ds", source: "sub-dist-urban-n", target: "sub-dist-urban-s", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2 }, label: "220 MW Tie", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-di-dt", source: "sub-dist-ind-1", target: "sub-dist-tech", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2 }, label: "310 MW Tie", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-dh-da", source: "sub-dist-harbor", target: "sub-dist-airport", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2 }, label: "250 MW Tie", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },

  // --- Col 5 (Distribution) -> Col 6 (Critical & Urban Load Sinks) ---
  // Dual-Fed Trauma Hospital Feeds
  { id: "e-d1-hosp1-primary", source: "sub-dist-metro-1", target: "load-hospital-metro", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 3 }, label: "Hospital A (85 MW)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-d2-hosp1-backup", source: "sub-dist-metro-2", target: "load-hospital-metro", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Dual Backup", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  { id: "e-dn-hosp2-primary", source: "sub-dist-urban-n", target: "load-hospital-north", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 2.5 }, label: "Hospital B (65 MW)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-d1-hosp2-backup", source: "sub-dist-metro-1", target: "load-hospital-north", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Dual Backup", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  // Dual-Fed Cloud Data Center & AI GPU Supercluster
  { id: "e-dt-dc-primary", source: "sub-dist-tech", target: "load-datacenter-cloud", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 3 }, label: "Cloud DC (340 MW)", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },
  { id: "e-d2-dc-backup", source: "sub-dist-metro-2", target: "load-datacenter-cloud", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Tier-IV Backup", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },

  { id: "e-dt-ai-primary", source: "sub-dist-tech", target: "load-ai-supercluster", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 3.5 }, label: "AI GPU Cluster (420 MW)", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },
  { id: "e-di-ai-backup", source: "sub-dist-ind-1", target: "load-ai-supercluster", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Dual Backup", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },

  // Commercial CBD, Industrial & Residential Feeds
  { id: "e-d1-cbd", source: "sub-dist-metro-1", target: "load-city-cbd", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 3.5 }, label: "Metro CBD (1,140 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-d2-cbd", source: "sub-dist-metro-2", target: "load-city-cbd", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "CBD Feeder B", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-di-ind", source: "sub-dist-ind-1", target: "load-industrial-heavy", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 3 }, label: "Industrial (780 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-dh-ind", source: "sub-dist-harbor", target: "load-industrial-heavy", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Heavy Tie", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-ds-res", source: "sub-dist-urban-s", target: "load-residential-metro", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Residential (520 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-dn-res", source: "sub-dist-urban-n", target: "load-residential-metro", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Feeder 2", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-da-rail", source: "sub-dist-airport", target: "load-transit-rail", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Rail Traction (390 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-dh-rail", source: "sub-dist-harbor", target: "load-transit-rail", type: "smoothstep", animated: false, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 1.5, strokeDasharray: "5,5" }, label: "Port Tie", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
];

interface GridTopologyFlowProps {
  nodes?: Node[];
  edges?: Edge[];
  frequencyHz?: number | null;
  isSimulating?: boolean;
  onSimulate?: () => void;
}

export const GridTopologyFlow: React.FC<GridTopologyFlowProps> = ({
  nodes: propNodes,
  edges: propEdges,
  frequencyHz = 50.02,
  isSimulating: propIsSimulating,
  onSimulate,
}) => {
  const [nodes, setNodes] = useState<Node[]>(propNodes && propNodes.length > 0 ? propNodes : defaultInitialNodes);
  const [edges, setEdges] = useState<Edge[]>(propEdges && propEdges.length > 0 ? propEdges : defaultInitialEdges);
  const [localSimulating, setLocalSimulating] = useState(false);

  useEffect(() => {
    if (propNodes && propNodes.length > 0) {
      setNodes(propNodes);
    }
  }, [propNodes]);

  useEffect(() => {
    if (propEdges && propEdges.length > 0) {
      setEdges(propEdges);
    }
  }, [propEdges]);

  const isSimulating = propIsSimulating !== undefined ? propIsSimulating : localSimulating;

  const handleSimulateClick = () => {
    if (onSimulate) {
      onSimulate();
    } else {
      setLocalSimulating(!localSimulating);
    }
  };

  const nodeTypes = useMemo(
    () => ({
      solar: SolarNode,
      wind: WindNode,
      thermal: ThermalNode,
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
                LIVE GRID TOPOLOGY TWIN (50-NODE ENTERPRISE NETWORK)
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                50 BUSES • 80+ LINES
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Intricate 50-node digital twin network: 8 solar/wind plants, 8 base/peakers, 8 step-up & BESS buffers, 10 400kV bulk rings, 8 distribution feeders, and 8 critical hospital/AI/CBD loads.
            </p>
          </div>
        </div>

        {/* Live Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>50 NODES | 80+ BRANCHES</span>
          </div>

          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>FLOW RATE: {frequencyHz !== null && frequencyHz !== undefined ? `${frequencyHz.toFixed(2)} Hz` : "50.02 Hz"}</span>
          </div>

          <button
            onClick={handleSimulateClick}
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

      {/* React Flow Canvas Container (Expanded Dimensions for 50 Nodes) */}
      <div className="h-[750px] w-full relative bg-tech-grid">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.08 }}
          minZoom={0.15}
          maxZoom={1.8}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1e293b" gap={20} size={1.2} />
          
          {/* Controls placed top-right */}
          <Controls position="top-right" showInteractive={false} />
          
          {/* High-Resolution MiniMap for the 50-node Grid */}
          <MiniMap
            position="bottom-right"
            nodeColor={(n) => {
              if (n.type === "solar") return "#f59e0b";
              if (n.type === "wind") return "#06b6d4";
              if (n.type === "thermal") return "#f97316";
              if (n.type === "battery") return "#10b981";
              if (n.type === "substation") return "#3b82f6";
              if (n.type === "cityLoad") return "#f43f5e";
              return "#64748b";
            }}
            maskColor="rgba(7, 9, 14, 0.8)"
            maskStrokeColor="#f59e0b"
            maskStrokeWidth={1.5}
            zoomable
            pannable
            style={{
              width: 230,
              height: 140,
              backgroundColor: "#090d16",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              borderRadius: "8px",
              margin: 12,
            }}
          />
        </ReactFlow>

        {/* Legend Overlay at bottom left */}
        <div className="absolute bottom-3 left-3 z-10 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-lg p-2.5 shadow-xl text-[11px] font-mono text-slate-300 space-y-1 hidden md:block">
          <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1 flex items-center justify-between gap-4">
            <span>GRID ASSET LEGEND (50 NODES)</span>
            <span className="text-amber-400">EXPANDED TWIN</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10px]">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>Solar PV (4 Plants)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Wind Power (4 Farms)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-orange-400"></span>
              <span>Thermal & Nuclear (8 Units)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>BESS Storage (4 Units)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              <span>400kV & 220kV Hubs (22 Subs)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span>Hospitals & Sinks (8 Loads)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
