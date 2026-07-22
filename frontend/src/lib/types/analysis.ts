/** Inventory-driven AI analysis report types */

export type FindingStatus = "covered" | "unknown" | "risk" | "positive";
export type EvidenceStrength = "strong" | "moderate" | "weak" | "none";

export interface AnalysisFinding {
  item_id: string;
  label?: string;
  status: FindingStatus;
  note: string;
  /** What evidence supports the conclusion */
  evidence: string;
  /** What still must be verified on-site / via documents */
  required_proof: string;
  evidence_strength: EvidenceStrength;
  confidence: number | null;
}

export interface AnalysisCategoryResult {
  category_id: string;
  title: string;
  score: number | null;
  summary: string;
  findings: AnalysisFinding[];
  coverage: {
    total: number;
    evaluated: number;
    unknown: number;
    risk: number;
    positive: number;
  };
}

export interface InventoryAnalysisReport {
  property_id: string;
  executive_summary: string;
  overall_score: number;
  confidence_score: number;
  methodology: string;
  categories: AnalysisCategoryResult[];
  risks: string[];
  opportunities: string[];
  data_gaps: string[];
  due_diligence: string[];
  recommendation: string;
  model: string;
  generated_at: string;
  source: "openai";
  inventory_version: number;
  inventory_items_total: number;
  inventory_items_covered: number;
}

export interface AnalysisPropertySnapshot {
  id: string;
  title: string;
  description?: string | null;
  property_type?: string | null;
  property_category?: string | null;
  status?: string | null;
  pricing?: {
    sale_price?: string | number | null;
    rental_price?: string | number | null;
    currency?: string | null;
  } | null;
  location?: {
    province?: string | null;
    district?: string | null;
    neighborhood?: string | null;
    latitude?: string | number | null;
    longitude?: string | number | null;
  } | null;
  building?: Record<string, unknown> | null;
  features?: Record<string, unknown> | null;
  amenities?: string[] | null;
  tags?: string[] | null;
}

/** Legacy external service stubs (kept for optional future wiring). */
export interface ValuationSummary {
  property_id: string;
  estimated_value: number | null;
  currency: string;
  confidence: number | null;
  as_of: string | null;
  source: string;
}

export interface RiskSummary {
  property_id: string;
  overall_score: number | null;
  earthquake_risk: string | null;
  flood_risk: string | null;
  as_of: string | null;
  source: string;
}

export interface InvestmentSummary {
  property_id: string;
  expected_yield_pct: number | null;
  hold_period_years: number | null;
  recommendation: string | null;
  as_of: string | null;
  source: string;
}

export interface PropertyAnalysisBundle {
  valuation: ValuationSummary | null;
  risk: RiskSummary | null;
  investment: InvestmentSummary | null;
  unavailable: string[];
}
