import React from "react";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = "",
  hoverable = false,
}) => {
  return (
    <div
      className={`bg-slate-950/90 rounded-xl border border-slate-800 shadow-xl backdrop-blur-xl text-slate-100 overflow-hidden transition-all duration-200 ${
        hoverable ? "hover:shadow-2xl hover:border-slate-700" : ""
      } ${className}`}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<{
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
  className?: string;
}> = ({ title, subtitle, action, className = "" }) => {
  return (
    <div
      className={`p-5 pb-3 flex items-start justify-between border-b border-slate-800/80 ${className}`}
    >
      <div>
        <h3 className="text-base font-semibold text-slate-100 tracking-tight">
          {title}
        </h3>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};

export const CardContent: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = "" }) => {
  return <div className={`p-5 ${className}`}>{children}</div>;
};
