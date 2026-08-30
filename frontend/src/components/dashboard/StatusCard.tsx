import React from "react";
import { GridSystemStatus } from "@/types/dashboard";
import { Card, CardHeader, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ActivityIcon } from "@/components/ui/Icons";

interface StatusCardProps {
  status: GridSystemStatus;
}

export const StatusCard: React.FC<StatusCardProps> = ({ status }) => {
  const loadPercentage = Math.round(
    (status.currentLoadMW / status.totalCapacityMW) * 100
  );

  return (
    <Card className="h-full flex flex-col justify-between">
      <CardHeader
        title="Grid Telemetry & System Health"
        subtitle="Real-time telemetry stream and stability indicators"
        action={
          <Badge variant="success" dot>
            {status.lastSyncTime}
          </Badge>
        }
      />
      <CardContent className="space-y-5">
        {/* Frequency & Voltage Tolerance indicator */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
            <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 block">
              Grid Frequency
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-lg font-bold text-slate-800">
                {status.frequencyHz.toFixed(2)}
              </span>
              <span className="text-xs text-slate-500">Hz</span>
            </div>
            <span className="text-[11px] text-emerald-600 font-medium">
              Nominal (50.0 Hz)
            </span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg">
            <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 block">
              Stability Index
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-lg font-bold text-slate-800">
                {status.stabilityIndexPercent}%
              </span>
            </div>
            <span className="text-[11px] text-emerald-600 font-medium">
              Optimal Resilience
            </span>
          </div>

          <div className="p-3 bg-slate-50 border border-slate-100 rounded-lg col-span-2 sm:col-span-1">
            <span className="text-[11px] font-medium uppercase tracking-wider text-slate-500 block">
              Active Alerts
            </span>
            <div className="mt-1 flex items-baseline gap-1">
              <span className="text-lg font-bold text-slate-800">
                {status.activeAlertsCount}
              </span>
              <span className="text-xs text-slate-500">Critical</span>
            </div>
            <span className="text-[11px] text-slate-500 font-medium">
              0 contingencies
            </span>
          </div>
        </div>

        {/* Real-time Load Bar */}
        <div>
          <div className="flex justify-between items-center text-xs font-medium text-slate-700 mb-1.5">
            <span>Current Real-Time Load</span>
            <span>
              {status.currentLoadMW.toLocaleString()} MW /{" "}
              {status.totalCapacityMW.toLocaleString()} MW ({loadPercentage}%)
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
            <div
              className={`h-2.5 rounded-full transition-all duration-500 ${
                loadPercentage > 90
                  ? "bg-rose-500"
                  : loadPercentage > 75
                  ? "bg-blue-600"
                  : "bg-emerald-500"
              }`}
              style={{ width: `${loadPercentage}%` }}
            />
          </div>
        </div>

        {/* Engine Footnote */}
        <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100">
          <div className="flex items-center gap-1.5">
            <ActivityIcon size={14} className="text-blue-600" />
            <span>Digital Twin Simulation State: Ready</span>
          </div>
          <span className="font-mono text-[11px] text-slate-400">
            Node Sync: 100%
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
