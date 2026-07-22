"use client";

import { useEffect, useState } from "react";
import { getPropertyAnalysis } from "@/lib/api/analysis";
import type { PropertyAnalysisBundle } from "@/lib/types/analysis";

export function usePropertyAnalysis(propertyId: string | undefined) {
  const [data, setData] = useState<PropertyAnalysisBundle | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!propertyId) return;
    let cancelled = false;
    setLoading(true);
    getPropertyAnalysis(propertyId)
      .then((bundle) => {
        if (!cancelled) setData(bundle);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [propertyId]);

  return { analysis: data, loading };
}
