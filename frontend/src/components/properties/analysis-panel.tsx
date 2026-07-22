"use client";

import { LineChart, ShieldAlert, TrendingUp } from "lucide-react";
import { usePropertyAnalysis } from "@/hooks/useAnalysis";
import { analysisServiceConfigured } from "@/lib/config/analysis";
import { formatPrice } from "@/lib/api/client";

interface AnalysisPanelProps {
  propertyId: string;
}

function Metric({
  icon: Icon,
  title,
  value,
  hint,
}: {
  icon: typeof TrendingUp;
  title: string;
  value: string;
  hint: string;
}) {
  return (
    <div className="rounded-xl border border-border/60 bg-muted/20 p-4">
      <div className="flex items-center gap-2 text-sm font-medium">
        <Icon className="h-4 w-4 text-primary" />
        {title}
      </div>
      <p className="mt-2 font-[family-name:var(--font-display)] text-xl font-semibold tracking-tight">
        {value}
      </p>
      <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
    </div>
  );
}

export function AnalysisPanel({ propertyId }: AnalysisPanelProps) {
  const { analysis, loading } = usePropertyAnalysis(propertyId);
  const anyConfigured =
    analysisServiceConfigured("valuation") ||
    analysisServiceConfigured("risk") ||
    analysisServiceConfigured("investment");

  if (!anyConfigured) {
    return (
      <div className="rounded-xl border border-dashed border-border/80 p-5 text-sm text-muted-foreground">
        Analysis APIs are not configured yet. Set{" "}
        <code className="text-xs">NEXT_PUBLIC_VALUATION_API_URL</code>,{" "}
        <code className="text-xs">NEXT_PUBLIC_RISK_API_URL</code>,{" "}
        <code className="text-xs">NEXT_PUBLIC_INVESTMENT_API_URL</code> (or{" "}
        <code className="text-xs">NEXT_PUBLIC_FINWARD_API_URL</code>) when those
        services are ready.
      </div>
    );
  }

  if (loading || !analysis) {
    return (
      <div className="rounded-xl border border-border/60 p-5 text-sm text-muted-foreground">
        Loading analysis…
      </div>
    );
  }

  const valuationValue =
    analysis.valuation?.estimated_value != null
      ? formatPrice(analysis.valuation.estimated_value, analysis.valuation.currency)
      : "—";
  const riskValue =
    analysis.risk?.overall_score != null
      ? `${analysis.risk.overall_score}/100`
      : analysis.risk?.earthquake_risk || "—";
  const yieldValue =
    analysis.investment?.expected_yield_pct != null
      ? `${analysis.investment.expected_yield_pct.toFixed(1)}%`
      : analysis.investment?.recommendation || "—";

  return (
    <div className="grid gap-3 sm:grid-cols-3">
      <Metric
        icon={TrendingUp}
        title="Valuation"
        value={valuationValue}
        hint={
          analysis.unavailable.includes("valuation")
            ? "Service URL missing"
            : analysis.valuation?.as_of
              ? `As of ${analysis.valuation.as_of}`
              : "No valuation returned"
        }
      />
      <Metric
        icon={ShieldAlert}
        title="Risk"
        value={String(riskValue)}
        hint={
          analysis.unavailable.includes("risk")
            ? "Service URL missing"
            : analysis.risk?.as_of
              ? `As of ${analysis.risk.as_of}`
              : "No risk score returned"
        }
      />
      <Metric
        icon={LineChart}
        title="Investment"
        value={String(yieldValue)}
        hint={
          analysis.unavailable.includes("investment")
            ? "Service URL missing"
            : analysis.investment?.as_of
              ? `As of ${analysis.investment.as_of}`
              : "No investment view returned"
        }
      />
    </div>
  );
}
