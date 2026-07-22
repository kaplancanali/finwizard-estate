import { loadSession } from "@/lib/auth/session";
import { ANALYSIS_ENV, analysisServiceConfigured } from "@/lib/config/analysis";
import type {
  InvestmentSummary,
  PropertyAnalysisBundle,
  RiskSummary,
  ValuationSummary,
} from "@/lib/types/analysis";

async function fetchJson<T>(url: string): Promise<T | null> {
  const headers: HeadersInit = { Accept: "application/json" };
  const token = loadSession()?.token;
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const res = await fetch(url, { headers, cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

function resolveBase(
  dedicated: string,
  gatewayPath: string
): string | null {
  if (dedicated) return dedicated;
  if (ANALYSIS_ENV.finwardApiBaseUrl) {
    return `${ANALYSIS_ENV.finwardApiBaseUrl}${gatewayPath}`;
  }
  return null;
}

export async function getValuationSummary(
  propertyId: string
): Promise<ValuationSummary | null> {
  const base = resolveBase(ANALYSIS_ENV.valuationBaseUrl, "/valuation");
  if (!base) return null;
  const data = await fetchJson<{ data?: ValuationSummary } | ValuationSummary>(
    `${base}/properties/${propertyId}/valuation`
  );
  if (!data) return null;
  return "data" in data && data.data ? data.data : (data as ValuationSummary);
}

export async function getRiskSummary(propertyId: string): Promise<RiskSummary | null> {
  const base = resolveBase(ANALYSIS_ENV.riskBaseUrl, "/risk");
  if (!base) return null;
  const data = await fetchJson<{ data?: RiskSummary } | RiskSummary>(
    `${base}/properties/${propertyId}/risk`
  );
  if (!data) return null;
  return "data" in data && data.data ? data.data : (data as RiskSummary);
}

export async function getInvestmentSummary(
  propertyId: string
): Promise<InvestmentSummary | null> {
  const base = resolveBase(ANALYSIS_ENV.investmentBaseUrl, "/investment");
  if (!base) return null;
  const data = await fetchJson<{ data?: InvestmentSummary } | InvestmentSummary>(
    `${base}/properties/${propertyId}/investment`
  );
  if (!data) return null;
  return "data" in data && data.data ? data.data : (data as InvestmentSummary);
}

export async function getPropertyAnalysis(
  propertyId: string
): Promise<PropertyAnalysisBundle> {
  const unavailable: string[] = [];

  if (!analysisServiceConfigured("valuation")) unavailable.push("valuation");
  if (!analysisServiceConfigured("risk")) unavailable.push("risk");
  if (!analysisServiceConfigured("investment")) unavailable.push("investment");

  const [valuation, risk, investment] = await Promise.all([
    unavailable.includes("valuation") ? null : getValuationSummary(propertyId),
    unavailable.includes("risk") ? null : getRiskSummary(propertyId),
    unavailable.includes("investment") ? null : getInvestmentSummary(propertyId),
  ]);

  return { valuation, risk, investment, unavailable };
}
