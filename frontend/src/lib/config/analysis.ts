/**
 * Downstream analysis service bases.
 * Leave empty until Valuation / Risk / Investment APIs are available.
 */
export const ANALYSIS_ENV = {
  valuationBaseUrl: process.env.NEXT_PUBLIC_VALUATION_API_URL?.replace(/\/$/, "") || "",
  riskBaseUrl: process.env.NEXT_PUBLIC_RISK_API_URL?.replace(/\/$/, "") || "",
  investmentBaseUrl: process.env.NEXT_PUBLIC_INVESTMENT_API_URL?.replace(/\/$/, "") || "",
  /** Optional unified gateway (used when a specific service URL is missing). */
  finwardApiBaseUrl: process.env.NEXT_PUBLIC_FINWARD_API_URL?.replace(/\/$/, "") || "",
} as const;

export function analysisServiceConfigured(
  service: "valuation" | "risk" | "investment"
): boolean {
  if (service === "valuation") {
    return Boolean(ANALYSIS_ENV.valuationBaseUrl || ANALYSIS_ENV.finwardApiBaseUrl);
  }
  if (service === "risk") {
    return Boolean(ANALYSIS_ENV.riskBaseUrl || ANALYSIS_ENV.finwardApiBaseUrl);
  }
  return Boolean(ANALYSIS_ENV.investmentBaseUrl || ANALYSIS_ENV.finwardApiBaseUrl);
}
