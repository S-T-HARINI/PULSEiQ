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

// 48-Node Meshed Multi-Bus Enterprise Grid Network
const defaultInitialNodes: Node[] = [
  // ================= COLUMN 1: RENEWABLE GENERATION (x: 40) =================
  {
    id: "solar-1",
    type: "solar",
    position: { x: 40, y: 40 },
    width: 210,
    height: 105,
    data: { label: "Desert Sun Alpha", type: "solar", output: "480 MW", capacity: "500 MW", status: "OPTIMAL" },
  },
  {
    id: "solar-2",
    type: "solar",
    position: { x: 40, y: 165 },
    width: 210,
    height: 105,
    data: { label: "Desert Sun Beta", type: "solar", output: "420 MW", capacity: "450 MW", status: "OPTIMAL" },
  },
  {
    id: "solar-3",
    type: "solar",
    position: { x: 40, y: 290 },
    width: 210,
    height: 105,
    data: { label: "Helios Solar North", type: "solar", output: "380 MW", capacity: "400 MW", status: "OPTIMAL" },
  },
  {
    id: "solar-4",
    type: "solar",
    position: { x: 40, y: 415 },
    width: 210,
    height: 105,
    data: { label: "Helios Solar South", type: "solar", output: "340 MW", capacity: "350 MW", status: "ONLINE" },
  },
  {
    id: "solar-5",
    type: "solar",
    position: { x: 40, y: 540 },
    width: 210,
    height: 105,
    data: { label: "Valley PV Park 1", type: "solar", output: "280 MW", capacity: "300 MW", status: "ONLINE" },
  },
  {
    id: "solar-6",
    type: "solar",
    position: { x: 40, y: 665 },
    width: 210,
    height: 105,
    data: { label: "Valley PV Park 2", type: "solar", output: "260 MW", capacity: "300 MW", status: "ONLINE" },
  },
  {
    id: "wind-1",
    type: "wind",
    position: { x: 40, y: 790 },
    width: 210,
    height: 105,
    data: { label: "Highland Wind Alpha", type: "wind", output: "420 MW", capacity: "450 MW", status: "OPTIMAL" },
  },
  {
    id: "wind-2",
    type: "wind",
    position: { x: 40, y: 915 },
    width: 210,
    height: 105,
    data: { label: "Highland Wind Beta", type: "wind", output: "390 MW", capacity: "400 MW", status: "OPTIMAL" },
  },
  {
    id: "wind-3",
    type: "wind",
    position: { x: 40, y: 1040 },
    width: 210,
    height: 105,
    data: { label: "Offshore Wind 1", type: "wind", output: "580 MW", capacity: "600 MW", status: "OPTIMAL" },
  },
  {
    id: "wind-4",
    type: "wind",
    position: { x: 40, y: 1165 },
    width: 210,
    height: 105,
    data: { label: "Offshore Wind 2", type: "wind", output: "520 MW", capacity: "550 MW", status: "ONLINE" },
  },
  {
    id: "wind-5",
    type: "wind",
    position: { x: 40, y: 1290 },
    width: 210,
    height: 105,
    data: { label: "Coastal Turbines North", type: "wind", output: "310 MW", capacity: "350 MW", status: "ONLINE" },
  },
  {
    id: "wind-6",
    type: "wind",
    position: { x: 40, y: 1415 },
    width: 210,
    height: 105,
    data: { label: "Ridge Crest Wind Farm", type: "wind", output: "360 MW", capacity: "400 MW", status: "ONLINE" },
  },

  // ================= COLUMN 2: THERMAL & STEP-UP HUBS (x: 400) =================
  {
    id: "thermal-1",
    type: "thermal",
    position: { x: 400, y: 40 },
    width: 210,
    height: 105,
    data: { label: "Combined Cycle Gas 1", type: "thermal", output: "650 MW", capacity: "700 MW", status: "ONLINE" },
  },
  {
    id: "thermal-2",
    type: "thermal",
    position: { x: 400, y: 220 },
    width: 210,
    height: 105,
    data: { label: "Combined Cycle Gas 2", type: "thermal", output: "580 MW", capacity: "600 MW", status: "ONLINE" },
  },
  {
    id: "thermal-3",
    type: "thermal",
    position: { x: 400, y: 400 },
    width: 210,
    height: 105,
    data: { label: "Gas Peaker Plant A", type: "thermal", output: "320 MW", capacity: "400 MW", status: "STANDBY" },
  },
  {
    id: "thermal-4",
    type: "thermal",
    position: { x: 400, y: 580 },
    width: 210,
    height: 105,
    data: { label: "Gas Peaker Plant B", type: "thermal", output: "280 MW", capacity: "350 MW", status: "STANDBY" },
  },
  {
    id: "sub-stepup-1",
    type: "substation",
    position: { x: 400, y: 760 },
    width: 220,
    height: 105,
    data: { label: "Solar Collector Hub 1", type: "substation", output: "900 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-stepup-2",
    type: "substation",
    position: { x: 400, y: 940 },
    width: 220,
    height: 105,
    data: { label: "Solar Collector Hub 2", type: "substation", output: "880 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-stepup-3",
    type: "substation",
    position: { x: 400, y: 1120 },
    width: 220,
    height: 105,
    data: { label: "Wind Collector Hub 1", type: "substation", output: "1,100 MW", voltage: "132/400 kV", status: "SYNC" },
  },
  {
    id: "sub-stepup-4",
    type: "substation",
    position: { x: 400, y: 1300 },
    width: 220,
    height: 105,
    data: { label: "Wind Collector Hub 2", type: "substation", output: "870 MW", voltage: "132/400 kV", status: "SYNC" },
  },

  // ================= COLUMN 3: BESS STORAGE & WEST SWITCHING (x: 760) =================
  {
    id: "bess-1",
    type: "battery",
    position: { x: 760, y: 40 },
    width: 210,
    height: 105,
    data: { label: "NeoStorage BESS 400MWh", type: "battery", output: "+180 MW", soc: "88.5%", status: "OPTIMAL" },
  },
  {
    id: "bess-2",
    type: "battery",
    position: { x: 760, y: 220 },
    width: 210,
    height: 105,
    data: { label: "GridReserve BESS 250MWh", type: "battery", output: "+120 MW", soc: "91.2%", status: "OPTIMAL" },
  },
  {
    id: "bess-3",
    type: "battery",
    position: { x: 760, y: 400 },
    width: 210,
    height: 105,
    data: { label: "Apex Megapack Alpha", type: "battery", output: "+95 MW", soc: "84.0%", status: "OPTIMAL" },
  },
  {
    id: "bess-4",
    type: "battery",
    position: { x: 760, y: 580 },
    width: 210,
    height: 105,
    data: { label: "Apex Megapack Beta", type: "battery", output: "+90 MW", soc: "82.5%", status: "OPTIMAL" },
  },
  {
    id: "bess-5",
    type: "battery",
    position: { x: 760, y: 760 },
    width: 210,
    height: 105,
    data: { label: "Highland BESS Buffer", type: "battery", output: "+75 MW", soc: "86.0%", status: "OPTIMAL" },
  },
  {
    id: "bess-6",
    type: "battery",
    position: { x: 760, y: 940 },
    width: 210,
    height: 105,
    data: { label: "Coastal BESS Buffer", type: "battery", output: "+60 MW", soc: "89.4%", status: "OPTIMAL" },
  },
  {
    id: "sub-west-1",
    type: "substation",
    position: { x: 760, y: 1120 },
    width: 220,
    height: 105,
    data: { label: "West Bulk Switching 400kV", type: "substation", output: "1,650 MW", voltage: "401.5 kV", status: "SYNC" },
  },
  {
    id: "sub-west-2",
    type: "substation",
    position: { x: 760, y: 1300 },
    width: 220,
    height: 105,
    data: { label: "North Bulk Switching 400kV", type: "substation", output: "1,420 MW", voltage: "402.0 kV", status: "SYNC" },
  },

  // ================= COLUMN 4: 400kV BULK TRUNK & INTERTIES (x: 1120) =================
  {
    id: "sub-hub-alpha",
    type: "substation",
    position: { x: 1120, y: 80 },
    width: 220,
    height: 105,
    data: { label: "Hub Substation Alpha 400kV", type: "substation", output: "2,100 MW", voltage: "401.8 kV", status: "SYNC" },
  },
  {
    id: "sub-hub-beta",
    type: "substation",
    position: { x: 1120, y: 320 },
    width: 220,
    height: 105,
    data: { label: "Hub Substation Beta 400kV", type: "substation", output: "1,950 MW", voltage: "400.9 kV", status: "SYNC" },
  },
  {
    id: "sub-hub-gamma",
    type: "substation",
    position: { x: 1120, y: 560 },
    width: 220,
    height: 105,
    data: { label: "Central Intertie Hub 400kV", type: "substation", output: "2,450 MW", voltage: "402.4 kV", status: "SYNC" },
  },
  {
    id: "sub-hub-delta",
    type: "substation",
    position: { x: 1120, y: 800 },
    width: 220,
    height: 105,
    data: { label: "South Bulk Hub 400kV", type: "substation", output: "1,820 MW", voltage: "399.8 kV", status: "SYNC" },
  },
  {
    id: "sub-hub-epsilon",
    type: "substation",
    position: { x: 1120, y: 1040 },
    width: 220,
    height: 105,
    data: { label: "Regional Ring Hub 400kV", type: "substation", output: "1,780 MW", voltage: "400.2 kV", status: "SYNC" },
  },
  {
    id: "sub-hub-zeta",
    type: "substation",
    position: { x: 1120, y: 1280 },
    width: 220,
    height: 105,
    data: { label: "Cross-Border Tie 400kV", type: "substation", output: "1,550 MW", voltage: "401.1 kV", status: "SYNC" },
  },

  // ================= COLUMN 5: 220kV / 132kV DISTRIBUTION HUBS (x: 1480) =================
  {
    id: "sub-dist-1",
    type: "substation",
    position: { x: 1480, y: 80 },
    width: 220,
    height: 105,
    data: { label: "Metro Step-Down 220kV", type: "substation", output: "1,480 MW", voltage: "220.5 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-2",
    type: "substation",
    position: { x: 1480, y: 320 },
    width: 220,
    height: 105,
    data: { label: "North Urban Feeder 132kV", type: "substation", output: "980 MW", voltage: "132.2 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-3",
    type: "substation",
    position: { x: 1480, y: 560 },
    width: 220,
    height: 105,
    data: { label: "South Suburban Step-Down", type: "substation", output: "890 MW", voltage: "132.0 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-4",
    type: "substation",
    position: { x: 1480, y: 800 },
    width: 220,
    height: 105,
    data: { label: "Industrial Ring Substation", type: "substation", output: "1,120 MW", voltage: "220.1 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-5",
    type: "substation",
    position: { x: 1480, y: 1040 },
    width: 220,
    height: 105,
    data: { label: "Tech Corridor Substation", type: "substation", output: "760 MW", voltage: "132.4 kV", status: "SYNC" },
  },
  {
    id: "sub-dist-6",
    type: "substation",
    position: { x: 1480, y: 1280 },
    width: 220,
    height: 105,
    data: { label: "Harbor Logistics Substation", type: "substation", output: "840 MW", voltage: "132.1 kV", status: "SYNC" },
  },

  // ================= COLUMN 6: URBAN LOAD SINKS & CRITICAL LOADS (x: 1840) =================
  {
    id: "load-hospital",
    type: "cityLoad",
    position: { x: 1840, y: 80 },
    width: 210,
    height: 105,
    data: { label: "Metro General Hospital", type: "cityLoad", load: "125 MW", status: "OPTIMAL" },
  },
  {
    id: "load-city-center",
    type: "cityLoad",
    position: { x: 1840, y: 270 },
    width: 210,
    height: 105,
    data: { label: "Metro Central CBD", type: "cityLoad", load: "1,140 MW", status: "OPTIMAL" },
  },
  {
    id: "load-datacenter",
    type: "cityLoad",
    position: { x: 1840, y: 460 },
    width: 210,
    height: 105,
    data: { label: "Financial Cloud Data Center", type: "cityLoad", load: "340 MW", status: "OPTIMAL" },
  },
  {
    id: "load-industrial",
    type: "cityLoad",
    position: { x: 1840, y: 650 },
    width: 210,
    height: 105,
    data: { label: "Heavy Manufacturing Park", type: "cityLoad", load: "780 MW", status: "OPTIMAL" },
  },
  {
    id: "load-residential-n",
    type: "cityLoad",
    position: { x: 1840, y: 840 },
    width: 210,
    height: 105,
    data: { label: "North Residential Sector", type: "cityLoad", load: "460 MW", status: "OPTIMAL" },
  },
  {
    id: "load-residential-s",
    type: "cityLoad",
    position: { x: 1840, y: 1030 },
    width: 210,
    height: 105,
    data: { label: "South Suburban District", type: "cityLoad", load: "390 MW", status: "OPTIMAL" },
  },
  {
    id: "load-harbor",
    type: "cityLoad",
    position: { x: 1840, y: 1220 },
    width: 210,
    height: 105,
    data: { label: "Port Terminal & Logistics", type: "cityLoad", load: "310 MW", status: "OPTIMAL" },
  },
  {
    id: "load-transit",
    type: "cityLoad",
    position: { x: 1840, y: 1410 },
    width: 210,
    height: 105,
    data: { label: "High-Speed Rail Traction", type: "cityLoad", load: "235 MW", status: "OPTIMAL" },
  },
];

// 65+ Interconnected Power Flow Transmission Lines
const defaultInitialEdges: Edge[] = [
  // --- Col 1 (Solar) -> Col 2 (Step-Up) ---
  { id: "e-s1-su1", source: "solar-1", target: "sub-stepup-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "480 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s2-su1", source: "solar-2", target: "sub-stepup-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "420 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s3-su2", source: "solar-3", target: "sub-stepup-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "380 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s4-su2", source: "solar-4", target: "sub-stepup-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "340 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s5-su2", source: "solar-5", target: "sub-stepup-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "280 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },
  { id: "e-s6-su1", source: "solar-6", target: "sub-stepup-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-amber", style: { stroke: "#f59e0b", strokeWidth: 2 }, label: "260 MW", labelStyle: { fill: "#fbbf24", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f59e0b50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f59e0b" } },

  // --- Col 1 (Wind) -> Col 2 (Wind Collector) ---
  { id: "e-w1-su3", source: "wind-1", target: "sub-stepup-3", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2 }, label: "420 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w2-su3", source: "wind-2", target: "sub-stepup-3", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2 }, label: "390 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w3-su3", source: "wind-3", target: "sub-stepup-3", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "580 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w4-su4", source: "wind-4", target: "sub-stepup-4", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2.5 }, label: "520 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w5-su4", source: "wind-5", target: "sub-stepup-4", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2 }, label: "310 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },
  { id: "e-w6-su4", source: "wind-6", target: "sub-stepup-4", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-cyan", style: { stroke: "#06b6d4", strokeWidth: 2 }, label: "360 MW", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#06b6d450", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#06b6d4" } },

  // --- Col 2 (Thermal & Step-Up) -> Col 3 (BESS & West Switching) ---
  { id: "e-th1-ha", source: "thermal-1", target: "sub-hub-alpha", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 3 }, label: "650 MW (Gas CC)", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-th2-hb", source: "thermal-2", target: "sub-hub-beta", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 2.5 }, label: "580 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-th3-b3", source: "thermal-3", target: "bess-3", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 2 }, label: "320 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },
  { id: "e-th4-b4", source: "thermal-4", target: "bess-4", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-orange", style: { stroke: "#f97316", strokeWidth: 2 }, label: "280 MW", labelStyle: { fill: "#fb923c", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f9731650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f97316" } },

  { id: "e-su1-w1", source: "sub-stepup-1", target: "sub-west-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "900 MW (400kV)", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-su2-w1", source: "sub-stepup-2", target: "sub-west-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "880 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-su3-w2", source: "sub-stepup-3", target: "sub-west-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,100 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-su4-w2", source: "sub-stepup-4", target: "sub-west-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "870 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },

  // --- Col 3 (BESS Storage) -> Col 4 (400kV Bulk Hubs) ---
  { id: "e-b1-ha", source: "bess-1", target: "sub-hub-alpha", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2.5 }, label: "+180 MW (BESS)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b2-hb", source: "bess-2", target: "sub-hub-beta", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+120 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b3-hg", source: "bess-3", target: "sub-hub-gamma", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+95 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b4-hd", source: "bess-4", target: "sub-hub-delta", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+90 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b5-he", source: "bess-5", target: "sub-hub-epsilon", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+75 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-b6-hz", source: "bess-6", target: "sub-hub-zeta", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-emerald", style: { stroke: "#10b981", strokeWidth: 2 }, label: "+60 MW", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  // --- West Switching -> 400kV Bulk Hubs ---
  { id: "e-w1-hg", source: "sub-west-1", target: "sub-hub-gamma", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,650 MW (Bulk Trunk)", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-w2-he", source: "sub-west-2", target: "sub-hub-epsilon", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3.5 }, label: "1,420 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },

  // --- 400kV Inter-Hub Meshed Ring Links ---
  { id: "e-ha-hb", source: "sub-hub-alpha", target: "sub-hub-beta", sourceHandle: "bottom", targetHandle: "top-in", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "850 MW Ring", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-hb-hg", source: "sub-hub-beta", target: "sub-hub-gamma", sourceHandle: "bottom", targetHandle: "top-in", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "920 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-hg-hd", source: "sub-hub-gamma", target: "sub-hub-delta", sourceHandle: "bottom", targetHandle: "top-in", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "1,140 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-hd-he", source: "sub-hub-delta", target: "sub-hub-epsilon", sourceHandle: "bottom", targetHandle: "top-in", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "980 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },
  { id: "e-he-hz", source: "sub-hub-epsilon", target: "sub-hub-zeta", sourceHandle: "bottom", targetHandle: "top-in", type: "smoothstep", animated: true, className: "animate-flow-blue", style: { stroke: "#3b82f6", strokeWidth: 3 }, label: "840 MW", labelStyle: { fill: "#93c5fa", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#3b82f650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" } },

  // --- Col 4 (400kV Bulk) -> Col 5 (Distribution Substations) ---
  { id: "e-ha-d1", source: "sub-hub-alpha", target: "sub-dist-1", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 3 }, label: "1,480 MW (220kV)", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-hb-d2", source: "sub-hub-beta", target: "sub-dist-2", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "980 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-hg-d3", source: "sub-hub-gamma", target: "sub-dist-3", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "890 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-hd-d4", source: "sub-hub-delta", target: "sub-dist-4", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 3 }, label: "1,120 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-he-d5", source: "sub-hub-epsilon", target: "sub-dist-5", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "760 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },
  { id: "e-hz-d6", source: "sub-hub-zeta", target: "sub-dist-6", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-purple", style: { stroke: "#8b5cf6", strokeWidth: 2.5 }, label: "840 MW", labelStyle: { fill: "#c4b5fd", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#8b5cf650", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#8b5cf6" } },

  // --- Col 5 (Distribution) -> Col 6 (Load Sinks & Critical Loads) ---
  // Dual-feed redundancy for Hospital & Data Center
  { id: "e-d1-hosp", source: "sub-dist-1", target: "load-hospital", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 3 }, label: "Hospital Feeder A (125 MW)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },
  { id: "e-d2-hosp", source: "sub-dist-2", target: "load-hospital", sourceHandle: "right", targetHandle: "top", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#10b981", strokeWidth: 2 }, label: "Feeder B (Standby)", labelStyle: { fill: "#34d399", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#10b98150", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" } },

  { id: "e-d1-city", source: "sub-dist-1", target: "load-city-center", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 3.5 }, label: "Metro CBD (1,140 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-d2-city", source: "sub-dist-2", target: "load-city-center", sourceHandle: "right", targetHandle: "top", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2 }, label: "CBD Feeder 2", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-d2-dc", source: "sub-dist-2", target: "load-datacenter", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 2.5 }, label: "Data Center (340 MW)", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },
  { id: "e-d3-dc", source: "sub-dist-3", target: "load-datacenter", sourceHandle: "right", targetHandle: "top", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#38bdf8", strokeWidth: 2 }, label: "Redundant Ring", labelStyle: { fill: "#38bdf8", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#38bdf850", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#38bdf8" } },

  { id: "e-d4-ind", source: "sub-dist-4", target: "load-industrial", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 3 }, label: "Industrial Park (780 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-d3-ind", source: "sub-dist-3", target: "load-industrial", sourceHandle: "right", targetHandle: "top", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2 }, label: "Heavy Tie", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-d3-resn", source: "sub-dist-3", target: "load-residential-n", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Residential (460 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-d4-ress", source: "sub-dist-4", target: "load-residential-s", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Suburban (390 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },

  { id: "e-d6-harb", source: "sub-dist-6", target: "load-harbor", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Harbor (310 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
  { id: "e-d5-tran", source: "sub-dist-5", target: "load-transit", sourceHandle: "right", targetHandle: "left", type: "smoothstep", animated: true, className: "animate-flow-rose", style: { stroke: "#f43f5e", strokeWidth: 2.5 }, label: "Rail Traction (235 MW)", labelStyle: { fill: "#fb7185", fontWeight: 700, fontSize: 10, fontFamily: "monospace" }, labelBgStyle: { fill: "#090d16", stroke: "#f43f5e50", strokeWidth: 1, rx: 4, ry: 4 }, labelBgPadding: [6, 4], markerEnd: { type: MarkerType.ArrowClosed, color: "#f43f5e" } },
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
                LIVE GRID TOPOLOGY TWIN (48-BUS ENTERPRISE NETWORK)
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                MESHED MESH TOPOLOGY
              </span>
            </div>
            <p className="text-xs text-slate-400 font-sans mt-0.5">
              Expansive 48-bus grid topology with 65+ transmission lines, N-1 ring branches, and dual-fed critical hospital loads.
            </p>
          </div>
        </div>

        {/* Live Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-mono text-slate-300">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>48 NODES | 65 LINES</span>
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

      {/* React Flow Canvas Container (Expanded Height for 48 Nodes) */}
      <div className="h-[680px] w-full relative bg-tech-grid">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.08 }}
          minZoom={0.2}
          maxZoom={1.8}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#1e293b" gap={20} size={1.2} />
          
          {/* Controls placed top-right */}
          <Controls position="top-right" showInteractive={false} />
          
          {/* High-Resolution MiniMap for the 48-node Grid */}
          <MiniMap
            position="bottom-right"
            nodeColor={(n) => {
              if (n.type === "solar") return "#f59e0b";
              if (n.type === "wind") return "#06b6d4";
              if (n.type === "thermal") return "#f97316";
              if (n.type === "battery") return "#10b981";
              if (n.type === "cityLoad") return "#f43f5e";
              return "#3b82f6";
            }}
            nodeStrokeColor={(n) => {
              if (n.type === "solar") return "#fbbf24";
              if (n.type === "wind") return "#38bdf8";
              if (n.type === "thermal") return "#fdba74";
              if (n.type === "battery") return "#34d399";
              if (n.type === "cityLoad") return "#fb7185";
              return "#60a5fa";
            }}
            nodeStrokeWidth={2}
            nodeBorderRadius={4}
            maskColor="rgba(7, 9, 14, 0.8)"
            maskStrokeColor="#f59e0b"
            maskStrokeWidth={1.5}
            zoomable
            pannable
            style={{
              width: 220,
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
            <span>GRID ASSET LEGEND (48 NODES)</span>
            <span className="text-amber-400">EXPANDED TWIN</span>
          </div>
          <div className="grid grid-cols-2 gap-x-3 gap-y-0.5 text-[10px]">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>Solar PV (6 Plants)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Wind Power (6 Farms)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-orange-400"></span>
              <span>Gas / Thermal (4 Units)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>BESS Storage (6 Units)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              <span>400kV Hubs (16 Subs)</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span>Urban Sinks (8 Loads)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
