export interface GridMetric {
  id: string;
  label: string;
  value: string;
  unit?: string;
  status: "nominal" | "warning" | "optimal" | "critical";
  delta?: string;
  deltaType?: "positive" | "negative" | "neutral";
  technicalDetail: string;
}

export interface TelemetryPoint {
  time: string;
  loadMW: number;
  generationMW: number;
  baselineMW: number;
  solarMW: number;
  windMW: number;
  thermalMW: number;
  bessMW: number;
  frequencyHz: number;
}

export interface SimulationModule {
  id: string;
  name: string;
  tag: string;
  status: "ONLINE" | "STANDBY" | "ANALYZING" | "READY";
  description: string;
  actionLabel: string;
  accentColor: "amber" | "cyan" | "emerald" | "blue" | "rose";
  stats: { label: string; value: string }[];
}
