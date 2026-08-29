"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { GridTelemetryMessage } from "@/types/api";

export type WebSocketStatus = "connecting" | "connected" | "disconnected" | "error";

export interface GridTelemetryData {
  message_type: string;
  timestamp: string;
  grid_status: "NORMAL" | "WARNING" | "ALERT" | "CRITICAL" | "CONTINGENCY";
  total_generation: number;
  total_demand: number;
  renewable_generation_percent: number;
  battery_soc: number;
  grid_risk_index: number;
  frequency_hz: number;
  line_utilization_avg?: number;
  affected_components?: string[];
  details?: Record<string, unknown>;
}

interface UseGridTelemetryOptions {
  enabled?: boolean;
  customUrl?: string;
  onMessage?: (data: GridTelemetryMessage) => void;
}

export function useGridTelemetry(options: UseGridTelemetryOptions | string = {}) {
  const resolvedOptions: UseGridTelemetryOptions =
    typeof options === "string" ? { customUrl: options } : options;

  const { enabled = true, customUrl, onMessage } = resolvedOptions;

  const [telemetry, setTelemetry] = useState<GridTelemetryMessage | null>(null);
  const [frequencyHz, setFrequencyHz] = useState<number | null>(50.02);
  const [status, setStatus] = useState<WebSocketStatus>("disconnected");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isUnmountingRef = useRef<boolean>(false);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const getWsUrl = useCallback(() => {
    if (customUrl) return customUrl;
    if (process.env.NEXT_PUBLIC_WS_URL) {
      return process.env.NEXT_PUBLIC_WS_URL;
    }
    if (typeof window !== "undefined") {
      const host = window.location.hostname || "localhost";
      return `ws://${host}:8000/ws/grid`;
    }
    return "ws://localhost:8000/ws/grid";
  }, [customUrl]);

  const connect = useCallback(() => {
    if (!enabled || isUnmountingRef.current || typeof window === "undefined") return;

    if (
      wsRef.current &&
      (wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    try {
      setStatus("connecting");
      const url = getWsUrl();
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        if (isUnmountingRef.current) {
          ws.close();
          return;
        }
        setStatus("connected");
        setError(null);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as GridTelemetryMessage & {
            frequency?: number;
          };
          if (data && (data.message_type === "grid_telemetry" || data.frequency_hz !== undefined)) {
            const freq = data.frequency_hz ?? data.frequency ?? null;
            if (typeof freq === "number") {
              setFrequencyHz(freq);
            }
            setTelemetry(data);
            setLastUpdated(new Date());
            if (onMessage) {
              onMessage(data);
            }
          }
        } catch {
          // ignore non-json frames or heartbeat acks
        }
      };

      ws.onerror = () => {
        setStatus("error");
        setError("WebSocket connection error");
      };

      ws.onclose = () => {
        setStatus("disconnected");
        wsRef.current = null;

        if (enabled && !isUnmountingRef.current && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 10000);
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Failed to connect WebSocket");
    }
  }, [enabled, getWsUrl, onMessage]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setStatus("disconnected");
  }, []);

  useEffect(() => {
    isUnmountingRef.current = false;
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      isUnmountingRef.current = true;
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    telemetry,
    frequencyHz: frequencyHz ?? 50.02,
    isConnected: status === "connected",
    status,
    lastUpdated,
    reconnect: connect,
    disconnect,
    error,
  };
}
