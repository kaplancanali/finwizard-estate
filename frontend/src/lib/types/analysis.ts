/** Analysis / intelligence service contracts (filled when platform APIs are wired). */

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
