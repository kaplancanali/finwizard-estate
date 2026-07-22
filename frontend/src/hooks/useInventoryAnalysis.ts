"use client";

import { useCallback, useEffect, useState } from "react";
import type {
  AnalysisPropertySnapshot,
  InventoryAnalysisReport,
} from "@/lib/types/analysis";

const cacheKey = (propertyId: string) => `torkam.analysis.${propertyId}`;

function loadCached(propertyId: string): InventoryAnalysisReport | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(cacheKey(propertyId));
    if (!raw) return null;
    return JSON.parse(raw) as InventoryAnalysisReport;
  } catch {
    return null;
  }
}

function saveCached(report: InventoryAnalysisReport) {
  try {
    sessionStorage.setItem(cacheKey(report.property_id), JSON.stringify(report));
  } catch {
    // ignore quota errors
  }
}

export function useInventoryAnalysis(property: AnalysisPropertySnapshot | null) {
  const propertyId = property?.id;
  const [report, setReport] = useState<InventoryAnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!propertyId) return;
    setReport(loadCached(propertyId));
    setError(null);
  }, [propertyId]);

  const generate = useCallback(async () => {
    if (!property?.id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/analysis/report", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ property }),
      });
      const payload = await res.json();
      if (!res.ok) {
        throw new Error(payload?.error?.message || `HTTP ${res.status}`);
      }
      const data = payload.data as InventoryAnalysisReport;
      setReport(data);
      saveCached(data);
      return data;
    } catch (err) {
      const message = err instanceof Error ? err.message : "Analiz oluşturulamadı";
      setError(message);
      return undefined;
    } finally {
      setLoading(false);
    }
  }, [property]);

  const clear = useCallback(() => {
    if (!propertyId) return;
    sessionStorage.removeItem(cacheKey(propertyId));
    setReport(null);
    setError(null);
  }, [propertyId]);

  return { report, loading, error, generate, clear };
}
