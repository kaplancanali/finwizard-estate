"use client";

import {
  AlertTriangle,
  CheckCircle2,
  Download,
  FileText,
  HelpCircle,
  Loader2,
  RefreshCcw,
  ShieldAlert,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useInventoryAnalysis } from "@/hooks/useInventoryAnalysis";
import { downloadAnalysisPdf } from "@/lib/analysis/pdf";
import type {
  AnalysisPropertySnapshot,
  EvidenceStrength,
  FindingStatus,
} from "@/lib/types/analysis";
import type { Property } from "@/lib/types/api";

interface AnalysisPanelProps {
  property: Property;
}

function toSnapshot(property: Property): AnalysisPropertySnapshot {
  return {
    id: property.id,
    title: property.title,
    description: property.description,
    property_type: property.property_type,
    property_category: property.property_category,
    status: property.status,
    pricing: property.pricing,
    location: property.location,
    building: property.building as Record<string, unknown> | null,
    features: property.features as Record<string, unknown> | null,
    amenities: property.amenities,
    tags: property.tags,
  };
}

function statusMeta(status: FindingStatus): {
  label: string;
  className: string;
  Icon: typeof CheckCircle2;
} {
  switch (status) {
    case "positive":
      return {
        label: "Olumlu",
        className: "bg-emerald-50 text-emerald-800 border-emerald-200",
        Icon: CheckCircle2,
      };
    case "risk":
      return {
        label: "Risk",
        className: "bg-rose-50 text-rose-800 border-rose-200",
        Icon: AlertTriangle,
      };
    case "covered":
      return {
        label: "Değerlendirildi",
        className: "bg-sky-50 text-sky-800 border-sky-200",
        Icon: TrendingUp,
      };
    default:
      return {
        label: "Kanıt yok",
        className: "bg-amber-50 text-amber-900 border-amber-200",
        Icon: HelpCircle,
      };
  }
}

function strengthLabel(s: EvidenceStrength): string {
  switch (s) {
    case "strong":
      return "Güçlü kanıt";
    case "moderate":
      return "Orta kanıt";
    case "weak":
      return "Zayıf kanıt";
    default:
      return "Kanıt yok";
  }
}

export function AnalysisPanel({ property }: AnalysisPanelProps) {
  const snapshot = toSnapshot(property);
  const { report, loading, error, generate, clear } = useInventoryAnalysis(snapshot);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium">AI envanter due-diligence</p>
          <p className="text-xs text-muted-foreground">
            Tüm envanter maddeleri tek tek; kanıt + required proof + PDF.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {report && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadAnalysisPdf(report, property.title)}
                disabled={loading}
              >
                <Download className="mr-1.5 h-3.5 w-3.5" />
                PDF indir
              </Button>
              <Button variant="outline" size="sm" onClick={clear} disabled={loading}>
                <RefreshCcw className="mr-1.5 h-3.5 w-3.5" />
                Temizle
              </Button>
            </>
          )}
          <Button size="sm" onClick={() => void generate()} disabled={loading}>
            {loading ? (
              <Loader2 className="mr-1.5 h-3.5 w-3.5 animate-spin" />
            ) : (
              <Sparkles className="mr-1.5 h-3.5 w-3.5" />
            )}
            {report ? "Yeniden oluştur" : "Detaylı rapor oluştur"}
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {error}
        </div>
      )}

      {!report && !loading && !error && (
        <div className="rounded-xl border border-dashed border-border/80 p-5 text-sm text-muted-foreground">
          Detaylı rapor, envanterdeki her maddeyi tarar; kanıt yoksa “required proof” üretir. Üretim
          30–90 sn sürebilir.
        </div>
      )}

      {loading && (
        <div className="rounded-xl border border-border/60 p-5 text-sm text-muted-foreground flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          Tüm envanter maddeleri kanıt zorunluluğuyla taranıyor…
        </div>
      )}

      {report && (
        <div className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-border/60 bg-muted/20 p-4 text-center">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Genel skor</p>
              <p className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight">
                {report.overall_score}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">/ 100</p>
            </div>
            <div className="rounded-xl border border-border/60 bg-muted/20 p-4 text-center">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Güven</p>
              <p className="mt-2 font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight">
                {report.confidence_score}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">/ 100</p>
            </div>
            <div className="rounded-xl border border-border/60 bg-muted/20 p-4 text-center">
              <p className="text-xs uppercase tracking-wide text-muted-foreground">Envanter</p>
              <p className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight">
                {report.inventory_items_covered}/{report.inventory_items_total}
              </p>
              <p className="mt-1 text-[11px] text-muted-foreground">değerlendirilen madde</p>
            </div>
          </div>

          <div className="rounded-xl border border-border/60 bg-muted/10 p-4">
            <p className="text-sm font-medium flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              Yönetici özeti
            </p>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
              {report.executive_summary}
            </p>
            <p className="mt-3 text-[11px] text-muted-foreground">
              {report.model} · {new Date(report.generated_at).toLocaleString("tr-TR")} · v
              {report.inventory_version}
            </p>
          </div>

          <div className="rounded-xl border border-border/60 p-4">
            <p className="text-sm font-medium">Metodoloji</p>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
              {report.methodology}
            </p>
          </div>

          <div className="rounded-xl border border-border/60 p-4">
            <p className="text-sm font-medium flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-primary" />
              Tavsiye
            </p>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap">
              {report.recommendation}
            </p>
          </div>

          <div className="grid gap-3 lg:grid-cols-3">
            <div className="rounded-xl border border-rose-200/70 bg-rose-50/40 p-4">
              <p className="text-sm font-medium text-rose-950">Riskler</p>
              <ul className="mt-2 space-y-1.5 text-sm text-rose-900/90">
                {(report.risks.length ? report.risks : ["Belirgin risk belirtilmedi."]).map((r) => (
                  <li key={r} className="leading-snug">
                    · {r}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-emerald-200/70 bg-emerald-50/40 p-4">
              <p className="text-sm font-medium text-emerald-950">Fırsatlar</p>
              <ul className="mt-2 space-y-1.5 text-sm text-emerald-900/90">
                {(report.opportunities.length
                  ? report.opportunities
                  : ["Belirgin fırsat belirtilmedi."]
                ).map((o) => (
                  <li key={o} className="leading-snug">
                    · {o}
                  </li>
                ))}
              </ul>
            </div>
            <div className="rounded-xl border border-amber-200/70 bg-amber-50/40 p-4">
              <p className="text-sm font-medium text-amber-950">Veri boşlukları</p>
              <ul className="mt-2 space-y-1.5 text-sm text-amber-900/90">
                {(report.data_gaps.length ? report.data_gaps : ["Kritik boşluk listelenmedi."]).map(
                  (g) => (
                    <li key={g} className="leading-snug">
                      · {g}
                    </li>
                  )
                )}
              </ul>
            </div>
          </div>

          <div className="rounded-xl border border-border/60 p-4">
            <p className="text-sm font-medium">Due diligence checklist</p>
            <ul className="mt-2 space-y-1.5 text-sm text-muted-foreground">
              {(report.due_diligence.length
                ? report.due_diligence
                : ["Checklist üretilmedi."]
              ).map((d) => (
                <li key={d} className="leading-snug">
                  ☐ {d}
                </li>
              ))}
            </ul>
          </div>

          <div className="space-y-3">
            {report.categories.map((cat) => (
              <div key={cat.category_id} className="rounded-xl border border-border/60 p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-medium">{cat.title}</p>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono text-[10px]">
                      {cat.coverage.evaluated}/{cat.coverage.total} madde
                    </Badge>
                    <Badge variant="outline" className="font-mono">
                      {cat.score != null ? `${cat.score}/100` : "—"}
                    </Badge>
                  </div>
                </div>
                <p className="mt-2 text-sm text-muted-foreground whitespace-pre-wrap">{cat.summary}</p>
                <ul className="mt-3 space-y-2">
                  {cat.findings.map((f, idx) => {
                    const meta = statusMeta(f.status);
                    const Icon = meta.Icon;
                    return (
                      <li
                        key={`${f.item_id}-${idx}`}
                        className="rounded-lg border border-border/50 bg-background/60 px-3 py-2.5 text-sm"
                      >
                        <div className="flex gap-2">
                          <Icon className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                          <div className="min-w-0 flex-1 space-y-1.5">
                            <div className="flex flex-wrap items-center gap-2">
                              <span
                                className={`inline-flex rounded-md border px-1.5 py-0.5 text-[10px] font-medium ${meta.className}`}
                              >
                                {meta.label}
                              </span>
                              <span className="text-[10px] text-muted-foreground">
                                {strengthLabel(f.evidence_strength)}
                              </span>
                              {f.confidence != null && (
                                <span className="font-mono text-[10px] text-muted-foreground">
                                  conf {f.confidence}
                                </span>
                              )}
                              <span className="text-xs font-medium text-foreground/90">
                                {f.label || f.item_id}
                              </span>
                            </div>
                            <p className="text-xs leading-relaxed text-muted-foreground">{f.note}</p>
                            <p className="text-[11px] leading-relaxed">
                              <span className="font-medium text-foreground/80">Kanıt: </span>
                              <span className="text-muted-foreground">{f.evidence}</span>
                            </p>
                            <p className="text-[11px] leading-relaxed">
                              <span className="font-medium text-amber-900">İstenen kanıt: </span>
                              <span className="text-muted-foreground">{f.required_proof}</span>
                            </p>
                          </div>
                        </div>
                      </li>
                    );
                  })}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
