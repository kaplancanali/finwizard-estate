import { NextRequest, NextResponse } from "next/server";
import {
  categoriesForProperty,
  compactInventoryForPrompt,
} from "@/lib/analysis/inventory";
import type {
  AnalysisPropertySnapshot,
  InventoryAnalysisReport,
} from "@/lib/types/analysis";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export const maxDuration = 60;

const SYSTEM_PROMPT = `Sen Torkam / FINWARD için Türkiye'de gayrimenkul yatırım analisti bir asistansın.
Görevin: verilen İLAN verisini, verilen ENVANTER checklist'ine göre değerlendirip JSON rapor üretmek.

Kurallar:
- Uydurma veri üretme. İlanda olmayan maddeleri status="unknown" yap ve note'ta neyin eksik olduğunu yaz.
- Skorlar 0-100 arası integer olsun. Bilgi zayıfsa skoru düşür veya null bırakma; overall_score her zaman ver.
- Her kategori için kısa summary yaz. findings dizisinde en fazla 8 madde tut (en kritik olanlar).
- risks ve opportunities kısa Türkçe maddeler olsun.
- recommendation tek paragraf, aksiyon odaklı Türkçe.
- Yalnızca geçerli JSON döndür, markdown kullanma.`;

function buildUserPrompt(
  property: AnalysisPropertySnapshot,
  inventory: ReturnType<typeof compactInventoryForPrompt>
): string {
  return JSON.stringify(
    {
      task: "inventory_analysis_report",
      property,
      inventory_categories: inventory,
      output_schema: {
        executive_summary: "string",
        overall_score: "number 0-100",
        categories: [
          {
            category_id: "string",
            title: "string",
            score: "number 0-100",
            summary: "string",
            findings: [
              {
                item_id: "string",
                status: "covered|unknown|risk|positive",
                note: "string",
              },
            ],
          },
        ],
        risks: ["string"],
        opportunities: ["string"],
        recommendation: "string",
      },
    },
    null,
    2
  );
}

function safeParseReport(
  content: string,
  propertyId: string,
  model: string
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
    return {
      property_id: propertyId,
      executive_summary: String(raw.executive_summary),
      overall_score: Math.max(0, Math.min(100, Math.round(raw.overall_score))),
      categories: Array.isArray(raw.categories) ? raw.categories : [],
      risks: Array.isArray(raw.risks) ? raw.risks.map(String) : [],
      opportunities: Array.isArray(raw.opportunities)
        ? raw.opportunities.map(String)
        : [],
      recommendation: String(raw.recommendation || ""),
      model,
      generated_at: new Date().toISOString(),
      source: "openai",
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
        temperature: 0.3,
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
    const report = safeParseReport(content, property.id, model);
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

    // Ensure category titles from inventory when model omits them
    const titleById = Object.fromEntries(cats.map((c) => [c.id, c.title]));
    report.categories = report.categories.map((c) => ({
      ...c,
      title: c.title || titleById[c.category_id] || c.category_id,
    }));

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
