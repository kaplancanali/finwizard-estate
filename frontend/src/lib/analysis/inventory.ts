import inventory from "@/lib/analysis/inventory.json";
import type { AnalysisPropertySnapshot } from "@/lib/types/analysis";

export type InventoryCategory = {
  id: string;
  title: string;
  commercial: boolean;
  items: Array<{ id: string; label: string }>;
};

export type InventoryDoc = {
  version: number;
  source: string;
  categories: InventoryCategory[];
};

export const ANALYSIS_INVENTORY = inventory as InventoryDoc;

export function categoriesForProperty(
  property: AnalysisPropertySnapshot
): InventoryCategory[] {
  const category = (property.property_category || "").toLowerCase();
  const type = (property.property_type || "").toLowerCase();
  const isCommercial =
    category.includes("commercial") ||
    category.includes("industrial") ||
    ["office", "store", "warehouse", "factory", "hotel"].includes(type);

  return ANALYSIS_INVENTORY.categories.filter((c) =>
    isCommercial ? true : !c.commercial
  );
}

export function compactInventoryForPrompt(categories: InventoryCategory[]) {
  return categories.map((c) => ({
    id: c.id,
    title: c.title,
    items: c.items.map((i) => ({ id: i.id, label: i.label })),
  }));
}
