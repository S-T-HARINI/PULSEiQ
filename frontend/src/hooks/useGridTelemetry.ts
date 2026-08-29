"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { GridTelemetryMessage } from "@/types/api";

export type WebSocketStatus = "connecting" | "connected" | "disconnected" | "error";

interface UseGridTelemetryOptions {
  enabled?: boolean;
  onMessage?: (data: GridTelemetryMessage) => void;
}

export function useGridTelemetry(options: UseGridTelemetryOptions = {}) {
  const { enabled = true, onMessage } = options;
  const [telemetry, setTelemetry] = useState<GridTelemetryMessage | null>(null);
  const [status, setStatus] = useState<WebSocketStatus>("disconnected");
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const getWsUrl = useCallback(() => {
    if (process.env.NEXT_PUBLIC_WS_URL) {
      return process.env.NEXT_PUBLIC_WS_URL;
    }
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const wsProto = apiUrl.startsWith("https") ? "wss:" : "ws:";
    const host = apiUrl.replace(/^https?:\/\//, "");
    return `${wsProto}//${host}/ws/grid`;
  }, []);

  const connect = useCallback(() => {
    if (!enabled || typeof window === "undefined") return;

    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    try {
      setStatus("connecting");
      const url = getWsUrl();
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as GridTelemetryMessage;
          if (data && data.message_type === "grid_telemetry") {
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
      };

      ws.onclose = () => {
        setStatus("disconnected");
        wsRef.current = null;

        // Exponential backoff reconnect
        if (enabled && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 10000);
          reconnectAttempts.current += 1;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch {
      setStatus("error");
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
    if (enabled) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    telemetry,
    status,
    lastUpdated,
    reconnect: connect,
    disconnect,
  };
}
