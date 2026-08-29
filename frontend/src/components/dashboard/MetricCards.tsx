import React from "react";
import { MetricCardData } from "@/types/dashboard";
import { Card } from "@/components/ui/Card";
import {
  SubstationIcon,
  BoltIcon,
  ChartIcon,
  ShieldIcon,
  ActivityIcon,
} from "@/components/ui/Icons";

interface MetricCardsProps {
  metrics: MetricCardData[];
}

export const MetricCards: React.FC<MetricCardsProps> = ({ metrics }) => {
  const getIcon = (iconName?: string) => {
    switch (iconName) {
      case "substation":
        return <SubstationIcon size={20} className="text-blue-600" />;
      case "bolt":
        return <BoltIcon size={20} className="text-amber-500" />;
      case "chart":
        return <ChartIcon size={20} className="text-emerald-600" />;
      case "shield":
        return <ShieldIcon size={20} className="text-indigo-600" />;
      default:
        return <ActivityIcon size={20} className="text-blue-600" />;
    }
  };

  const getIconBg = (iconName?: string) => {
    switch (iconName) {
      case "substation":
        return "bg-blue-50 border-blue-100";
      case "bolt":
        return "bg-amber-50 border-amber-100";
      case "chart":
        return "bg-emerald-50 border-emerald-100";
      case "shield":
        return "bg-indigo-50 border-indigo-100";
      default:
        return "bg-blue-50 border-blue-100";
    }
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {metrics.map((metric) => (
        <Card
          key={metric.id}
          hoverable
          className="p-5 flex flex-col justify-between"
        >
          <div>
            {/* Header: Title & Icon */}
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {metric.title}
              </span>
              <div
                className={`p-2 rounded-lg border ${getIconBg(
                  metric.iconName
                )}`}
              >
                {getIcon(metric.iconName)}
              </div>
            </div>

            {/* Metric Value & Unit */}
            <div className="mt-3 flex items-baseline gap-2">
              <span className="text-2xl font-bold tracking-tight text-slate-900">
                {metric.value}
              </span>
              {metric.unit && (
                <span className="text-sm font-medium text-slate-500">
                  {metric.unit}
                </span>
              )}
            </div>
          </div>

          {/* Subtitle & Trend / Status */}
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            {metric.change && (
              <span
                className={`font-medium ${
                  metric.changeType === "positive"
                    ? "text-emerald-600"
                    : metric.changeType === "negative"
                    ? "text-rose-600"
                    : "text-slate-600"
                }`}
              >
                {metric.change}
              </span>
            )}
            {metric.subtitle && (
              <span className="text-slate-400 truncate max-w-[150px]" title={metric.subtitle}>
                {metric.subtitle}
              </span>
            )}
          </div>
        </Card>
      ))}
    </div>
  );
};
