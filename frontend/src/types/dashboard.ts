export interface MetricCardData {
  id: string;
  title: string;
  value: string;
  unit?: string;
  change?: string;
  changeType?: "positive" | "negative" | "neutral";
  subtitle?: string;
  status: "normal" | "warning" | "critical" | "optimal";
  iconName?: string;
}

export interface GridSystemStatus {
  engineStatus: "Active" | "Standby" | "Calibrating" | "Offline";
  lastSyncTime: string;
  frequencyHz: number;
  activeAlertsCount: number;
  totalSubstations: number;
  activeSubstations: number;
  totalCapacityMW: number;
  currentLoadMW: number;
  stabilityIndexPercent: number;
}
