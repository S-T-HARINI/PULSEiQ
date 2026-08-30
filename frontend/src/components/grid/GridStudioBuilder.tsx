"use client";

import React, { useState, useCallback, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  addEdge,
  useNodesState,
  useEdgesState,
  Connection,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  SolarNode,
  WindNode,
  ThermalNode,
  SubstationNode,
  BatteryNode,
  CityLoadNode,
} from "./CustomNodes";
import {
  CustomGridCreate,
  CustomGridUpdate,
  GridDetailResponse,
  GridNodeApi,
  GridEdgeApi,
  NodeType,
  NodeCriticality,
  NodeStatus,
  EdgeStatus,
} from "@/types/api";
import { pulseApi } from "@/lib/api";
import {
  Sun,
  Wind,
  Flame,
  BatteryCharging,
  Zap,
  Building2,
  ShieldAlert,
  Save,
  CheckCircle2,
  AlertTriangle,
  ArrowLeft,
  Trash2,
  Sparkles,
  Sliders,
  X,
} from "lucide-react";

const nodeTypes = {
  solar: SolarNode,
  wind: WindNode,
  thermal: ThermalNode,
  substation: SubstationNode,
  battery: BatteryNode,
  cityLoad: CityLoadNode,
};

interface GridStudioBuilderProps {
  initialGrid?: GridDetailResponse | null;
  onBack: () => void;
  onSaved: (gridId: string, activated?: boolean) => void;
}

export const GridStudioBuilder: React.FC<GridStudioBuilderProps> = ({
  initialGrid,
  onBack,
  onSaved,
}) => {
  const isEditing = Boolean(initialGrid);

  // Grid Metadata State
  const [gridId] = useState(
    initialGrid?.grid_id || `custom_grid_${Date.now().toString(36)}`
  );
  const [name, setName] = useState(
    initialGrid?.name || "New Custom Microgrid"
  );
  const [description, setDescription] = useState(
    initialGrid?.description || ""
  );

  // Initial React Flow Nodes conversion
  const initialNodes: Node[] = useMemo(() => {
    if (!initialGrid || !initialGrid.nodes || initialGrid.nodes.length === 0) {
      // Default blank starting layout with 3 connected demonstration components
      return [
        {
          id: "solar_gen_1",
          type: "solar",
          position: { x: 80, y: 120 },
          width: 215,
          height: 110,
          data: {
            label: "Solar Farm Alpha",
            type: "solar",
            nodeType: "solar_plant",
            capacity: "60 MW",
            capacity_mw: 60,
            output: "45 MW",
            current_output_mw: 45,
            status: "ONLINE",
            criticality: "medium",
            risk_score: 0.1,
          },
        },
        {
          id: "sub_hub_1",
          type: "substation",
          position: { x: 380, y: 120 },
          width: 225,
          height: 110,
          data: {
            label: "Central Step-Up Sub",
            type: "substation",
            nodeType: "substation",
            capacity: "150 MW",
            capacity_mw: 150,
            output: "45 MW",
            current_output_mw: 0,
            voltage: "220.0 kV",
            status: "SYNC",
            criticality: "high",
            risk_score: 0.1,
          },
        },
        {
          id: "hosp_load_1",
          type: "cityLoad",
          position: { x: 680, y: 120 },
          width: 215,
          height: 110,
          data: {
            label: "Regional Clinic",
            type: "cityLoad",
            nodeType: "critical_load",
            capacity: "30 MW",
            capacity_mw: 30,
            load: "25 MW",
            current_output_mw: 25,
            status: "ONLINE",
            criticality: "critical",
            risk_score: 0.05,
          },
        },
      ];
    }

    return initialGrid.nodes.map((n, idx) => {
      let uiType = "cityLoad";
      if (n.type === "solar_plant") uiType = "solar";
      else if (n.type === "wind_plant") uiType = "wind";
      else if (n.type === "conventional_generator") uiType = "thermal";
      else if (n.type === "battery") uiType = "battery";
      else if (n.type === "substation") uiType = "substation";

      return {
        id: n.id,
        type: uiType,
        position: {
          x: n.position?.x ?? (idx % 4) * 300 + 80,
          y: n.position?.y ?? Math.floor(idx / 4) * 160 + 100,
        },
        width: 215,
        height: 110,
        data: {
          label: n.name,
          type: uiType,
          nodeType: n.type,
          capacity: `${Math.round(n.capacity_mw)} MW`,
          capacity_mw: n.capacity_mw,
          output: `${Math.round(n.current_output_mw)} MW`,
          load: `${Math.round(n.current_output_mw)} MW`,
          current_output_mw: n.current_output_mw,
          voltage: `${n.metadata?.voltage_kv ?? 115.0} kV`,
          soc: `${n.metadata?.state_of_charge_percent ?? 75.0}%`,
          status: n.status.toUpperCase(),
          criticality: n.criticality,
          risk_score: n.risk_score,
        },
      };
    });
  }, [initialGrid]);

  // Initial React Flow Edges conversion
  const initialEdges: Edge[] = useMemo(() => {
    if (!initialGrid || !initialGrid.edges || initialGrid.edges.length === 0) {
      return [
        {
          id: "line_solar_sub",
          source: "solar_gen_1",
          target: "sub_hub_1",
          animated: true,
          style: { stroke: "#06b6d4", strokeWidth: 2 },
          data: { capacity_mw: 80, power_flow_mw: 45, resistance_ohms: 0.02, reactance_ohms: 0.08 },
        },
        {
          id: "line_sub_hosp",
          source: "sub_hub_1",
          target: "hosp_load_1",
          animated: true,
          style: { stroke: "#06b6d4", strokeWidth: 2 },
          data: { capacity_mw: 40, power_flow_mw: 25, resistance_ohms: 0.02, reactance_ohms: 0.08 },
        },
      ];
    }

    return initialGrid.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      animated: e.status === "normal",
      style: { stroke: "#06b6d4", strokeWidth: 2 },
      data: {
        capacity_mw: e.capacity_mw,
        power_flow_mw: e.power_flow_mw,
        resistance_ohms: e.resistance_ohms ?? 0.02,
        reactance_ohms: e.reactance_ohms ?? 0.08,
      },
    }));
  }, [initialGrid]);

  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Inspector & selection state
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);

  // Processing & feedback state
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  const [isActivating, setIsActivating] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);
  const [saveSuccessMessage, setSaveSuccessMessage] = useState<string | null>(null);

  // Active selected node & edge objects
  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) || null,
    [nodes, selectedNodeId]
  );
  const selectedEdge = useMemo(
    () => edges.find((e) => e.id === selectedEdgeId) || null,
    [edges, selectedEdgeId]
  );

  // Connecting handles
  const onConnect = useCallback(
    (params: Connection) => {
      if (!params.source || !params.target || params.source === params.target) {
        return;
      }
      const newEdge: Edge = {
        id: `line_${params.source}_to_${params.target}_${Date.now().toString(36)}`,
        source: params.source,
        target: params.target,
        animated: true,
        style: { stroke: "#06b6d4", strokeWidth: 2 },
        data: {
          capacity_mw: 100.0,
          power_flow_mw: 20.0,
          resistance_ohms: 0.02,
          reactance_ohms: 0.08,
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
      setValidationErrors([]);
    },
    [setEdges]
  );

  // Add Component to Canvas
  const handleAddComponent = (typeKey: NodeType) => {
    const timestamp = Date.now().toString(36).slice(-4);
    let uiType = "cityLoad";
    let defaultName = "New Node";
    let defaultCap = 100;
    let defaultOutput = 50;
    let defaultCrit = "medium";
    let voltage = "115.0 kV";
    let soc = "80.0%";

    switch (typeKey) {
      case "solar_plant":
        uiType = "solar";
        defaultName = `Solar Array ${timestamp}`;
        defaultCap = 50;
        defaultOutput = 40;
        break;
      case "wind_plant":
        uiType = "wind";
        defaultName = `Wind Farm ${timestamp}`;
        defaultCap = 80;
        defaultOutput = 60;
        break;
      case "conventional_generator":
        uiType = "thermal";
        defaultName = `Gas Peaker ${timestamp}`;
        defaultCap = 250;
        defaultOutput = 180;
        break;
      case "battery":
        uiType = "battery";
        defaultName = `BESS Unit ${timestamp}`;
        defaultCap = 40;
        defaultOutput = 20;
        soc = "85.0%";
        break;
      case "substation":
        uiType = "substation";
        defaultName = `Substation ${timestamp}`;
        defaultCap = 300;
        defaultOutput = 0;
        defaultCrit = "high";
        voltage = "220.0 kV";
        break;
      case "critical_load":
        uiType = "cityLoad";
        defaultName = `Hospital / DC ${timestamp}`;
        defaultCap = 30;
        defaultOutput = 25;
        defaultCrit = "critical";
        break;
      case "load":
      default:
        uiType = "cityLoad";
        defaultName = `City Load ${timestamp}`;
        defaultCap = 120;
        defaultOutput = 85;
        defaultCrit = "low";
        break;
    }

    const newNodeId = `node_${typeKey}_${timestamp}`;
    const offset = (nodes.length % 5) * 40;

    const newNode: Node = {
      id: newNodeId,
      type: uiType,
      position: { x: 120 + offset, y: 140 + offset },
      width: 215,
      height: 110,
      data: {
        label: defaultName,
        type: uiType,
        nodeType: typeKey,
        capacity: `${defaultCap} MW`,
        capacity_mw: defaultCap,
        output: `${defaultOutput} MW`,
        load: `${defaultOutput} MW`,
        current_output_mw: defaultOutput,
        voltage,
        soc,
        status: "ONLINE",
        criticality: defaultCrit,
        risk_score: 0.1,
      },
    };

    setNodes((nds) => [...nds, newNode]);
    setSelectedNodeId(newNodeId);
    setSelectedEdgeId(null);
    setValidationErrors([]);
  };

  // Delete selected node or edge
  const handleDeleteSelected = () => {
    if (selectedNodeId) {
      setNodes((nds) => nds.filter((n) => n.id !== selectedNodeId));
      setEdges((eds) =>
        eds.filter(
          (e) => e.source !== selectedNodeId && e.target !== selectedNodeId
        )
      );
      setSelectedNodeId(null);
    } else if (selectedEdgeId) {
      setEdges((eds) => eds.filter((e) => e.id !== selectedEdgeId));
      setSelectedEdgeId(null);
    }
  };

  // Update selected Node properties
  const handleUpdateNodeProp = (key: string, value: unknown) => {
    if (!selectedNodeId) return;
    setNodes((nds) =>
      nds.map((n) => {
        if (n.id !== selectedNodeId) return n;
        const updatedData = { ...n.data, [key]: value };

        // Keep label and output/capacity formatted strings synchronized
        if (key === "label") updatedData.label = String(value);
        if (key === "capacity_mw") updatedData.capacity = `${value} MW`;
        if (key === "current_output_mw") {
          updatedData.output = `${value} MW`;
          updatedData.load = `${value} MW`;
        }

        return {
          ...n,
          data: updatedData,
        };
      })
    );
  };

  // Update selected Edge properties
  const handleUpdateEdgeProp = (key: string, value: unknown) => {
    if (!selectedEdgeId) return;
    setEdges((eds) =>
      eds.map((e) => {
        if (e.id !== selectedEdgeId) return e;
        return {
          ...e,
          data: {
            ...e.data,
            [key]: value,
          },
        };
      })
    );
  };

  // Client-Side Topological Validation
  const validateTopology = (): string[] => {
    const errors: string[] = [];
    const nodeIds = new Set(nodes.map((n) => n.id));

    if (nodes.length === 0) {
      errors.push("Grid must contain at least one node or substation.");
    }

    if (!name.trim()) {
      errors.push("Grid name cannot be blank.");
    }

    nodes.forEach((n) => {
      const cap = Number(n.data.capacity_mw ?? 0);
      if (cap < 0) {
        errors.push(`Node '${n.data.label || n.id}' has negative capacity.`);
      }
      const out = Number(n.data.current_output_mw ?? 0);
      if (out < 0) {
        errors.push(`Node '${n.data.label || n.id}' has negative output/demand.`);
      }
    });

    edges.forEach((e) => {
      if (!nodeIds.has(e.source)) {
        errors.push(`Transmission line '${e.id}' references missing source node '${e.source}'.`);
      }
      if (!nodeIds.has(e.target)) {
        errors.push(`Transmission line '${e.id}' references missing target node '${e.target}'.`);
      }
      const cap = Number(e.data?.capacity_mw ?? 0);
      if (cap <= 0) {
        errors.push(`Transmission line '${e.id}' has non-positive thermal capacity (${cap} MW).`);
      }
    });

    return errors;
  };

  // Construct payload conforming to backend GridNode / GridEdge schemas
  const buildPayload = () => {
    const apiNodes: GridNodeApi[] = nodes.map((n) => {
      const rawType = (n.data.nodeType as NodeType) || (
        n.type === "solar"
          ? "solar_plant"
          : n.type === "wind"
          ? "wind_plant"
          : n.type === "thermal"
          ? "conventional_generator"
          : n.type === "battery"
          ? "battery"
          : n.type === "substation"
          ? "substation"
          : "load"
      );

      const cap = Number(n.data.capacity_mw ?? 100);
      const out = Number(n.data.current_output_mw ?? 50);
      const crit = (n.data.criticality as NodeCriticality) || "medium";
      const risk = Number(n.data.risk_score ?? 0.1);

      return {
        id: n.id,
        name: String(n.data.label || n.id),
        type: rawType,
        capacity_mw: cap,
        current_output_mw: out,
        status: "online" as NodeStatus,
        criticality: crit,
        utilization_percent: cap > 0 ? Number(((out / cap) * 100).toFixed(2)) : 0,
        risk_score: risk,
        position: { x: Math.round(n.position.x), y: Math.round(n.position.y) },
        metadata: {
          voltage_kv: n.data.voltage ? parseFloat(String(n.data.voltage)) : 115.0,
          state_of_charge_percent: n.data.soc ? parseFloat(String(n.data.soc)) : 75.0,
        },
      };
    });

    const apiEdges: GridEdgeApi[] = edges.map((e) => {
      const cap = Number(e.data?.capacity_mw ?? 100);
      const flow = Number(e.data?.power_flow_mw ?? 20);
      const res = Number(e.data?.resistance_ohms ?? 0.02);
      const react = Number(e.data?.reactance_ohms ?? 0.08);

      return {
        id: e.id,
        source: e.source,
        target: e.target,
        capacity_mw: cap,
        power_flow_mw: flow,
        utilization_percent: cap > 0 ? Number(((flow / cap) * 100).toFixed(2)) : 0,
        status: "normal" as EdgeStatus,
        risk_score: 0.1,
        resistance_ohms: res,
        reactance_ohms: react,
        metadata: {},
      };
    });

    return { apiNodes, apiEdges };
  };

  // Save Grid handler
  const handleSaveGrid = async (andActivate: boolean = false) => {
    setApiError(null);
    setSaveSuccessMessage(null);

    const errors = validateTopology();
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }

    setValidationErrors([]);
    setIsSaving(true);
    if (andActivate) setIsActivating(true);

    try {
      const { apiNodes, apiEdges } = buildPayload();

      if (isEditing) {
        const updatePayload: CustomGridUpdate = {
          name,
          description,
          nodes: apiNodes,
          edges: apiEdges,
        };
        await pulseApi.updateCustomGrid(gridId, updatePayload);
      } else {
        const createPayload: CustomGridCreate = {
          grid_id: gridId,
          name,
          description,
          nodes: apiNodes,
          edges: apiEdges,
        };
        await pulseApi.createCustomGrid(createPayload);
      }

      if (andActivate) {
        await pulseApi.setActiveGrid(gridId);
        setSaveSuccessMessage(`Grid '${name}' successfully saved and activated!`);
      } else {
        setSaveSuccessMessage(`Grid '${name}' saved to digital twin directory.`);
      }

      setTimeout(() => {
        onSaved(gridId, andActivate);
      }, 800);
    } catch (err) {
      setApiError((err as Error).message || "Failed to save custom grid.");
    } finally {
      setIsSaving(false);
      setIsActivating(false);
    }
  };

  return (
    <div className="space-y-4">
      {/* Top Action Bar */}
      <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-4 sm:p-5 backdrop-blur-2xl shadow-2xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        {/* Left: Back button & Name Editor */}
        <div className="flex items-center gap-3 w-full lg:w-auto">
          <button
            onClick={onBack}
            className="p-2.5 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-800 text-slate-400 hover:text-slate-200 transition-all cursor-pointer shrink-0"
            title="Back to Directory"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div className="space-y-1 flex-1 min-w-[240px]">
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="bg-transparent text-base sm:text-lg font-black font-mono text-slate-100 uppercase tracking-tight border-b border-transparent hover:border-slate-700 focus:border-amber-500 focus:outline-none transition-all w-full"
              placeholder="ENTER GRID NAME..."
            />
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="bg-transparent text-xs text-slate-400 font-sans border-b border-transparent hover:border-slate-800 focus:border-slate-600 focus:outline-none transition-all w-full"
              placeholder="Add optional digital twin description..."
            />
          </div>
        </div>

        {/* Center: Component Quick Counts */}
        <div className="flex items-center gap-3 text-xs font-mono text-slate-400 bg-slate-900/80 px-4 py-2 rounded-xl border border-slate-800/80">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-cyan-400" />
            <span className="text-slate-200 font-bold">{nodes.length}</span>
            <span>NODES</span>
          </div>
          <span className="text-slate-700">|</span>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span className="text-slate-200 font-bold">{edges.length}</span>
            <span>LINES</span>
          </div>
        </div>

        {/* Right: Validation & Save Actions */}
        <div className="flex items-center gap-2 w-full lg:w-auto justify-end">
          <button
            onClick={() => {
              const errs = validateTopology();
              setValidationErrors(errs);
              if (errs.length === 0) {
                setSaveSuccessMessage("Topological checks passed. Ready to save.");
                setTimeout(() => setSaveSuccessMessage(null), 3000);
              }
            }}
            className="px-3.5 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-300 font-mono text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
            <span>VALIDATE</span>
          </button>

          <button
            onClick={() => handleSaveGrid(false)}
            disabled={isSaving}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-100 font-mono text-xs font-bold transition-all cursor-pointer flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5 text-amber-400" />
            <span>{isSaving && !isActivating ? "SAVING..." : "SAVE GRID"}</span>
          </button>

          <button
            onClick={() => handleSaveGrid(true)}
            disabled={isSaving || isActivating}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 via-amber-400 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 text-slate-950 font-mono text-xs font-black transition-all cursor-pointer shadow-[0_0_20px_rgba(245,158,11,0.25)] flex items-center gap-2 disabled:opacity-50"
          >
            {isActivating ? (
              <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>SAVE & ACTIVATE</span>
          </button>
        </div>
      </div>

      {/* Validation & Feedback Banners */}
      {validationErrors.length > 0 && (
        <div className="rounded-2xl border border-rose-500/40 bg-rose-950/30 p-4 text-xs font-mono text-rose-300 space-y-1.5 backdrop-blur-xl">
          <div className="flex items-center gap-2 font-bold text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <span>TOPOLOGICAL VALIDATION ERRORS ({validationErrors.length})</span>
          </div>
          <ul className="list-disc list-inside space-y-1 pl-1 text-[11px] text-rose-300/90">
            {validationErrors.map((err, i) => (
              <li key={i}>{err}</li>
            ))}
          </ul>
        </div>
      )}

      {apiError && (
        <div className="rounded-2xl border border-rose-500/40 bg-rose-950/30 p-4 text-xs font-mono text-rose-300 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 font-bold text-rose-400">
            <AlertTriangle className="w-4 h-4" />
            <span>{apiError}</span>
          </div>
          <button
            onClick={() => setApiError(null)}
            className="text-rose-400 hover:text-white p-1"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {saveSuccessMessage && (
        <div className="rounded-2xl border border-emerald-500/40 bg-emerald-950/30 p-4 text-xs font-mono text-emerald-300 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{saveSuccessMessage}</span>
        </div>
      )}

      {/* Main Studio Canvas & Inspector Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Left 3 Columns: Palette Bar & React Flow Canvas */}
        <div className="lg:col-span-3 space-y-3">
          {/* Component Palette Toolbar */}
          <div className="rounded-xl border border-slate-800/90 bg-[#090d16]/95 p-2.5 backdrop-blur-xl flex items-center gap-2 overflow-x-auto">
            <span className="text-[10px] font-mono font-bold text-slate-500 uppercase px-2 shrink-0">
              ADD ASSET:
            </span>

            <button
              onClick={() => handleAddComponent("conventional_generator")}
              className="px-3 py-1.5 rounded-lg bg-orange-950/40 hover:bg-orange-950/70 border border-orange-500/40 text-orange-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <Flame className="w-3.5 h-3.5" />
              <span>Generator</span>
            </button>

            <button
              onClick={() => handleAddComponent("solar_plant")}
              className="px-3 py-1.5 rounded-lg bg-amber-950/40 hover:bg-amber-950/70 border border-amber-500/40 text-amber-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <Sun className="w-3.5 h-3.5" />
              <span>Solar PV</span>
            </button>

            <button
              onClick={() => handleAddComponent("wind_plant")}
              className="px-3 py-1.5 rounded-lg bg-cyan-950/40 hover:bg-cyan-950/70 border border-cyan-500/40 text-cyan-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <Wind className="w-3.5 h-3.5" />
              <span>Wind Farm</span>
            </button>

            <button
              onClick={() => handleAddComponent("battery")}
              className="px-3 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-950/70 border border-emerald-500/40 text-emerald-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <BatteryCharging className="w-3.5 h-3.5" />
              <span>BESS Battery</span>
            </button>

            <button
              onClick={() => handleAddComponent("substation")}
              className="px-3 py-1.5 rounded-lg bg-blue-950/40 hover:bg-blue-950/70 border border-blue-500/40 text-blue-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>Substation</span>
            </button>

            <button
              onClick={() => handleAddComponent("load")}
              className="px-3 py-1.5 rounded-lg bg-rose-950/40 hover:bg-rose-950/70 border border-rose-500/40 text-rose-400 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <Building2 className="w-3.5 h-3.5" />
              <span>Normal Load</span>
            </button>

            <button
              onClick={() => handleAddComponent("critical_load")}
              className="px-3 py-1.5 rounded-lg bg-red-950/60 hover:bg-red-950/90 border border-red-500/50 text-red-300 font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shrink-0"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-red-400" />
              <span>Critical Load</span>
            </button>
          </div>

          {/* Interactive React Flow Canvas */}
          <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 overflow-hidden shadow-2xl h-[620px] relative">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              onNodeClick={(_, node) => {
                setSelectedNodeId(node.id);
                setSelectedEdgeId(null);
              }}
              onEdgeClick={(_, edge) => {
                setSelectedEdgeId(edge.id);
                setSelectedNodeId(null);
              }}
              onPaneClick={() => {
                setSelectedNodeId(null);
                setSelectedEdgeId(null);
              }}
              fitView
              fitViewOptions={{ padding: 0.1 }}
              minZoom={0.2}
              maxZoom={1.8}
              proOptions={{ hideAttribution: true }}
            >
              <Background color="#1e293b" gap={20} size={1.2} />
              <Controls position="top-right" showInteractive={false} />
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
                style={{
                  width: 180,
                  height: 110,
                  backgroundColor: "#090d16",
                  border: "1px solid rgba(255, 255, 255, 0.15)",
                  borderRadius: "8px",
                  margin: 12,
                }}
              />
            </ReactFlow>

            {/* Instruction Overlay */}
            <div className="absolute top-3 left-3 z-10 bg-slate-900/90 backdrop-blur-md border border-slate-800 rounded-lg px-3 py-1.5 text-[11px] font-mono text-slate-400 pointer-events-none">
              Drag nodes • Drag from handles to connect lines • Click component to edit
            </div>
          </div>
        </div>

        {/* Right 1 Column: Property Inspector Panel */}
        <div className="rounded-2xl border border-slate-800/90 bg-[#090d16]/95 p-5 backdrop-blur-2xl shadow-xl flex flex-col justify-between space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-amber-400" />
                <h3 className="text-xs font-mono font-bold text-slate-200 uppercase tracking-wide">
                  PROPERTY INSPECTOR
                </h3>
              </div>
              {(selectedNodeId || selectedEdgeId) && (
                <button
                  onClick={() => {
                    setSelectedNodeId(null);
                    setSelectedEdgeId(null);
                  }}
                  className="text-slate-500 hover:text-slate-300 p-1"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {selectedNode ? (
              /* Node Inspector */
              <div className="space-y-3.5 font-mono text-xs">
                <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  <span className="text-[10px] text-slate-500">TYPE:</span>
                  <span className="font-bold text-amber-400 uppercase">
                    {String(selectedNode.data.nodeType || selectedNode.type)}
                  </span>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-bold">COMPONENT NAME</label>
                  <input
                    type="text"
                    value={String(selectedNode.data.label || "")}
                    onChange={(e) => handleUpdateNodeProp("label", e.target.value)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">CAPACITY (MW)</label>
                    <input
                      type="number"
                      min="0"
                      value={Number(selectedNode.data.capacity_mw ?? 100)}
                      onChange={(e) => handleUpdateNodeProp("capacity_mw", parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">
                      {selectedNode.type === "cityLoad" ? "DEMAND (MW)" : "OUTPUT (MW)"}
                    </label>
                    <input
                      type="number"
                      min="0"
                      value={Number(selectedNode.data.current_output_mw ?? 50)}
                      onChange={(e) => handleUpdateNodeProp("current_output_mw", parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                </div>

                {selectedNode.type === "battery" && (
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">STATE OF CHARGE (%)</label>
                    <input
                      type="text"
                      value={String(selectedNode.data.soc || "80.0%")}
                      onChange={(e) => handleUpdateNodeProp("soc", e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                )}

                {selectedNode.type === "substation" && (
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">VOLTAGE CLASS</label>
                    <input
                      type="text"
                      value={String(selectedNode.data.voltage || "220.0 kV")}
                      onChange={(e) => handleUpdateNodeProp("voltage", e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                )}

                {selectedNode.type === "cityLoad" && (
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">CRITICALITY LEVEL</label>
                    <select
                      value={String(selectedNode.data.criticality || "medium")}
                      onChange={(e) => handleUpdateNodeProp("criticality", e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                    >
                      <option value="low">Low Priority</option>
                      <option value="medium">Medium Priority</option>
                      <option value="high">High Priority</option>
                      <option value="critical">Critical Tier-1 Load</option>
                    </select>
                  </div>
                )}

                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-bold">FAILURE PROBABILITY (0 - 1)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    value={Number(selectedNode.data.risk_score ?? 0.1)}
                    onChange={(e) => handleUpdateNodeProp("risk_score", parseFloat(e.target.value) || 0.1)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-amber-500 focus:outline-none"
                  />
                </div>
              </div>
            ) : selectedEdge ? (
              /* Edge Inspector */
              <div className="space-y-3.5 font-mono text-xs">
                <div className="p-2.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                  <div className="text-[10px] text-slate-500">TRANSMISSION LINE ID:</div>
                  <div className="font-bold text-cyan-400 truncate">{selectedEdge.id}</div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[10px]">
                  <div className="p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                    <span className="text-slate-500 block">SOURCE:</span>
                    <span className="text-slate-200 font-bold truncate block">{selectedEdge.source}</span>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-900/50 border border-slate-800">
                    <span className="text-slate-500 block">TARGET:</span>
                    <span className="text-slate-200 font-bold truncate block">{selectedEdge.target}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-bold">THERMAL CAPACITY (MW)</label>
                  <input
                    type="number"
                    min="1"
                    value={Number(selectedEdge.data?.capacity_mw ?? 100)}
                    onChange={(e) => handleUpdateEdgeProp("capacity_mw", parseFloat(e.target.value) || 1)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-cyan-500 focus:outline-none"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-[10px] text-slate-400 font-bold">ACTIVE FLOW (MW)</label>
                  <input
                    type="number"
                    min="0"
                    value={Number(selectedEdge.data?.power_flow_mw ?? 20)}
                    onChange={(e) => handleUpdateEdgeProp("power_flow_mw", parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-cyan-500 focus:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">RESISTANCE (Ω)</label>
                    <input
                      type="number"
                      step="0.005"
                      min="0.001"
                      value={Number(selectedEdge.data?.resistance_ohms ?? 0.02)}
                      onChange={(e) => handleUpdateEdgeProp("resistance_ohms", parseFloat(e.target.value) || 0.02)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-cyan-500 focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-400 font-bold">REACTANCE (Ω)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0.001"
                      value={Number(selectedEdge.data?.reactance_ohms ?? 0.08)}
                      onChange={(e) => handleUpdateEdgeProp("reactance_ohms", parseFloat(e.target.value) || 0.08)}
                      className="w-full px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-slate-100 focus:border-cyan-500 focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            ) : (
              /* Nothing selected guidance */
              <div className="p-6 text-center text-xs font-mono text-slate-500 space-y-2">
                <Sliders className="w-8 h-8 mx-auto text-slate-700" />
                <p>Click on any grid node or transmission edge on the canvas to inspect and edit its physical parameters.</p>
              </div>
            )}
          </div>

          {/* Delete Action when selected */}
          {(selectedNodeId || selectedEdgeId) && (
            <button
              onClick={handleDeleteSelected}
              className="w-full py-2 rounded-xl bg-rose-950/40 hover:bg-rose-950/70 border border-rose-500/40 text-rose-300 font-mono text-xs font-bold flex items-center justify-center gap-2 transition-all cursor-pointer"
            >
              <Trash2 className="w-4 h-4 text-rose-400" />
              <span>{selectedNodeId ? "DELETE COMPONENT" : "DELETE LINE"}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
