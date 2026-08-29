"use client";

import { useEffect, useState, useRef, useCallback } from "react";

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

export function useGridTelemetry(customUrl?: string) {
  const [telemetry, setTelemetry] = useState<GridTelemetryData | null>(null);
  const [frequencyHz, setFrequencyHz] = useState<number | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isUnmountingRef = useRef<boolean>(false);

  const getWsUrl = useCallback(() => {
    if (customUrl) return customUrl;
    if (process.env.NEXT_PUBLIC_WS_URL) return process.env.NEXT_PUBLIC_WS_URL;
    if (typeof window !== "undefined") {
      const host = window.location.hostname || "localhost";
      // Backend is on port 8000
      return `ws://${host}:8000/ws/grid`;
    }
    return "ws://localhost:8000/ws/grid";
  }, [customUrl]);

  const connect = useCallback(() => {
    if (isUnmountingRef.current) return;

    // Avoid duplicate connections if already open or connecting
    if (
      socketRef.current &&
      (socketRef.current.readyState === WebSocket.OPEN ||
        socketRef.current.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    try {
      const url = getWsUrl();
      const ws = new WebSocket(url);
      socketRef.current = ws;

      ws.onopen = () => {
        if (isUnmountingRef.current) {
          ws.close();
          return;
        }
        setIsConnected(true);
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.message_type === "grid_telemetry" || data.frequency_hz !== undefined || data.frequency !== undefined) {
            const freq = data.frequency_hz ?? data.frequency ?? null;
            if (typeof freq === "number") {
              setFrequencyHz(freq);
            }
            setTelemetry(data);
          }
        } catch {
          // Ignore unparseable frames
        }
      };

      ws.onerror = () => {
        setError("WebSocket connection error");
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        socketRef.current = null;

        // Automatically reconnect after delay if component is still mounted
        if (!isUnmountingRef.current) {
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
          }
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, 2000);
        }
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect WebSocket");
      setIsConnected(false);
      if (!isUnmountingRef.current) {
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, 3000);
      }
    }
  }, [getWsUrl]);

  useEffect(() => {
    isUnmountingRef.current = false;
    connect();

    return () => {
      isUnmountingRef.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [connect]);

  return {
    telemetry,
    frequencyHz,
    isConnected,
    error,
  };
}
