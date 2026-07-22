import { NextRequest, NextResponse } from "next/server";
import {
  ANALYSIS_INVENTORY,
  categoriesForProperty,
  compactInventoryForPrompt,
  type InventoryCategory,
} from "@/lib/analysis/inventory";
import type {
  AnalysisCategoryResult,
  AnalysisFinding,
  AnalysisPropertySnapshot,
  EvidenceStrength,
  FindingStatus,
  InventoryAnalysisReport,
} from "@/lib/types/analysis";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 120;

const SYSTEM_PROMPT = `Sen Torkam Holding için kıdemli bir gayrimenkul due-diligence analistisin.
Görevin: verilen İLAN verisini, verilen ENVANTER checklist'indeki **TÜM** maddeler için tek tek araştırıp kanıta dayalı JSON rapor üretmek.

ZORUNLU KURALLAR:
1) Envanterdeki her item_id için findings içinde TAM olarak bir kayıt üret. Atlama yok.
2) Uydurma rakam / belge / ölçüm uydurma. İlanda doğrudan destek yoksa status="unknown".
3) Her finding için şunlar zorunlu:
   - status: covered | unknown | risk | positive
   - note: kısa analitik yorum (Türkçe)
   - evidence: hangi ilan alanı / mantık bu sonuca götürdü (yoksa "İlanda kanıt yok")
   - required_proof: sahada / tapuda / belediyede / ekspertizde istenmesi gereken somut kanıt
   - evidence_strength: strong | moderate | weak | none
   - confidence: 0-100 integer
4) Kanıt dayat: positive/covered ancak evidence_strength en az "moderate" ise kabul et; aksi halde unknown veya risk.
5) Her kategori için detaylı summary (en az 3-4 cümle) ve score (0-100).
6) executive_summary uzun ve yapılandırılmış olsun (paragraflar).
7) methodology: hangi envanter çerçevelerinin kullanıldığını açıkla.
8) data_gaps: eksik kritik veriler listesi.
9) due_diligence: satın alma öncesi yapılacak kontrol checklist'i (somut adımlar).
10) risks / opportunities: kanıt veya boşluklara dayalı maddeler.
11) recommendation: net yatırım kararı çerçevesi (al / bekle / kaçın + koşullar).
12) Yalnızca geçerli JSON döndür; markdown yok.`;

function buildUserPrompt(
  property: AnalysisPropertySnapshot,
  inventory: ReturnType<typeof compactInventoryForPrompt>
): string {
  const totalItems = inventory.reduce((n, c) => n + c.items.length, 0);
  return JSON.stringify(
    {
      task: "full_inventory_due_diligence_report",
      instructions: {
        language: "tr",
        must_cover_every_inventory_item: true,
        total_inventory_items: totalItems,
        evidence_policy:
          "No fabricated evidence. Demand required_proof for every item lacking listing support.",
      },
      property,
      inventory_categories: inventory,
      output_schema: {
        executive_summary: "string (detailed)",
        overall_score: "number 0-100",
        confidence_score: "number 0-100",
        methodology: "string",
        categories: [
          {
            category_id: "string",
            title: "string",
            score: "number 0-100",
            summary: "string (detailed)",
            findings: [
              {
                item_id: "MUST match inventory item id",
                label: "string",
                status: "covered|unknown|risk|positive",
                note: "string",
                evidence: "string",
                required_proof: "string",
                evidence_strength: "strong|moderate|weak|none",
                confidence: "number 0-100",
              },
            ],
          },
        ],
        risks: ["string"],
        opportunities: ["string"],
        data_gaps: ["string"],
        due_diligence: ["string"],
        recommendation: "string",
      },
    },
    null,
    2
  );
}

function asStatus(value: unknown): FindingStatus {
  const v = String(value || "unknown");
  if (v === "covered" || v === "risk" || v === "positive" || v === "unknown") return v;
  return "unknown";
}

function asStrength(value: unknown): EvidenceStrength {
  const v = String(value || "none");
  if (v === "strong" || v === "moderate" || v === "weak" || v === "none") return v;
  return "none";
}

function normalizeFinding(
  raw: Partial<AnalysisFinding> | undefined,
  item: { id: string; label: string }
): AnalysisFinding {
  const status = asStatus(raw?.status);
  const evidence =
    String(raw?.evidence || "").trim() ||
    (status === "unknown" ? "İlanda bu maddeye dair kanıt yok." : "İlan verisinden dolaylı çıkarım.");
  const required_proof =
    String(raw?.required_proof || "").trim() ||
    `${item.label} için bağımsız belge / saha / resmi kayıt doğrulaması gerekli.`;
  let evidence_strength = asStrength(raw?.evidence_strength);
  if (status === "unknown") evidence_strength = "none";
  if ((status === "positive" || status === "covered") && evidence_strength === "none") {
    evidence_strength = "weak";
  }

  const confidenceRaw =
    typeof raw?.confidence === "number" ? raw.confidence : status === "unknown" ? 20 : 55;

  return {
    item_id: item.id,
    label: item.label,
    status,
    note:
      String(raw?.note || "").trim() ||
      (status === "unknown"
        ? `${item.label} ilan verisiyle doğrulanamadı; due-diligence şart.`
        : `${item.label} mevcut ilan bilgileriyle değerlendirildi.`),
    evidence,
    required_proof,
    evidence_strength,
    confidence: Math.max(0, Math.min(100, Math.round(confidenceRaw))),
  };
}

function coverageFor(findings: AnalysisFinding[]) {
  return {
    total: findings.length,
    evaluated: findings.filter((f) => f.status !== "unknown").length,
    unknown: findings.filter((f) => f.status === "unknown").length,
    risk: findings.filter((f) => f.status === "risk").length,
    positive: findings.filter((f) => f.status === "positive").length,
  };
}

function mergeFullInventory(
  rawCategories: AnalysisCategoryResult[] | undefined,
  inventory: InventoryCategory[]
): AnalysisCategoryResult[] {
  const byId = new Map((rawCategories || []).map((c) => [c.category_id, c]));

  return inventory.map((cat) => {
    const raw = byId.get(cat.id);
    const findingsByItem = new Map(
      (raw?.findings || []).map((f) => [f.item_id, f] as const)
    );
    const findings = cat.items.map((item) =>
      normalizeFinding(findingsByItem.get(item.id), item)
    );
    const coverage = coverageFor(findings);
    const score =
      typeof raw?.score === "number"
        ? Math.max(0, Math.min(100, Math.round(raw.score)))
        : Math.round(
            findings.reduce((s, f) => s + (f.confidence ?? 0), 0) / Math.max(findings.length, 1)
          );

    return {
      category_id: cat.id,
      title: raw?.title || cat.title,
      score,
      summary:
        String(raw?.summary || "").trim() ||
        `${cat.title}: ${coverage.evaluated}/${coverage.total} madde değerlendirildi; ${coverage.unknown} maddede kanıt eksik.`,
      findings,
      coverage,
    };
  });
}

function safeParseReport(
  content: string,
  propertyId: string,
  model: string,
  inventory: InventoryCategory[]
): InventoryAnalysisReport | null {
  try {
    const cleaned = content
      .trim()
      .replace(/^```json\s*/i, "")
      .replace(/^```\s*/i, "")
      .replace(/\s*```$/i, "");
    const raw = JSON.parse(cleaned) as Partial<InventoryAnalysisReport>;
    if (!raw.executive_summary || typeof raw.overall_score !== "number") {
      return null;
    }

    const categories = mergeFullInventory(raw.categories, inventory);
    const itemsTotal = categories.reduce((n, c) => n + c.findings.length, 0);
    const itemsCovered = categories.reduce(
      (n, c) => n + c.findings.filter((f) => f.status !== "unknown").length,
      0
    );

    return {
      property_id: propertyId,
      executive_summary: String(raw.executive_summary),
      overall_score: Math.max(0, Math.min(100, Math.round(raw.overall_score))),
      confidence_score: Math.max(
        0,
        Math.min(
          100,
          Math.round(
            typeof raw.confidence_score === "number"
              ? raw.confidence_score
              : (itemsCovered / Math.max(itemsTotal, 1)) * 100
          )
        )
      ),
      methodology:
        String(raw.methodology || "").trim() ||
        "Torkam Konut Envanter checklist’inin tamamı madde madde tarandı; kanıt yoksa unknown + required_proof üretildi.",
      categories,
      risks: Array.isArray(raw.risks) ? raw.risks.map(String) : [],
      opportunities: Array.isArray(raw.opportunities) ? raw.opportunities.map(String) : [],
      data_gaps: Array.isArray(raw.data_gaps) ? raw.data_gaps.map(String) : [],
      due_diligence: Array.isArray(raw.due_diligence) ? raw.due_diligence.map(String) : [],
      recommendation: String(raw.recommendation || ""),
      model,
      generated_at: new Date().toISOString(),
      source: "openai",
      inventory_version: ANALYSIS_INVENTORY.version,
      inventory_items_total: itemsTotal,
      inventory_items_covered: itemsCovered,
    };
  } catch {
    return null;
  }
}

export async function POST(request: NextRequest) {
  const apiKey = process.env.OPENAI_API_KEY?.trim();
  if (!apiKey) {
    return NextResponse.json(
      {
        error: {
          code: "OPENAI_NOT_CONFIGURED",
          message:
            "OPENAI_API_KEY is not set. Add it to frontend/.env.local or Vercel environment variables.",
        },
      },
      { status: 503 }
    );
  }

  let body: { property?: AnalysisPropertySnapshot };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json(
      { error: { code: "INVALID_JSON", message: "Request body must be JSON" } },
      { status: 400 }
    );
  }

  const property = body.property;
  if (!property?.id || !property?.title) {
    return NextResponse.json(
      {
        error: {
          code: "VALIDATION_ERROR",
          message: "property.id and property.title are required",
        },
      },
      { status: 422 }
    );
  }

  const model = process.env.OPENAI_MODEL?.trim() || "gpt-4o-mini";
  const cats = categoriesForProperty(property);
  const inventory = compactInventoryForPrompt(cats);

  try {
    const upstream = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        temperature: 0.2,
        response_format: { type: "json_object" },
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: buildUserPrompt(property, inventory) },
        ],
      }),
    });

    const payload = (await upstream.json()) as {
      error?: { message?: string };
      choices?: Array<{ message?: { content?: string } }>;
    };

    if (!upstream.ok) {
      return NextResponse.json(
        {
          error: {
            code: "OPENAI_ERROR",
            message: payload.error?.message || `OpenAI HTTP ${upstream.status}`,
          },
        },
        { status: 502 }
      );
    }

    const content = payload.choices?.[0]?.message?.content || "";
    const report = safeParseReport(content, property.id, model, cats);
    if (!report) {
      return NextResponse.json(
        {
          error: {
            code: "PARSE_ERROR",
            message: "Model response could not be parsed as analysis report",
          },
        },
        { status: 502 }
      );
    }

    return NextResponse.json({ data: report });
  } catch (err) {
    return NextResponse.json(
      {
        error: {
          code: "OPENAI_REQUEST_FAILED",
          message: err instanceof Error ? err.message : "OpenAI request failed",
        },
      },
      { status: 502 }
    );
  }
}
