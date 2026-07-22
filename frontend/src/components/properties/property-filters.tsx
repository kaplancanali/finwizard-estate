"use client";

import { Search, SlidersHorizontal, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useLookups } from "@/hooks/useProperties";
import { PropertySearchRequest } from "@/lib/types/api";
import { MotionDiv } from "@/lib/motion";
import { BrandLogo } from "@/components/ui-custom/brand-logo";
import { brand } from "@/lib/design-system";

interface PropertyFiltersProps {
  value: PropertySearchRequest;
  onChange: (value: PropertySearchRequest) => void;
  onSearch: () => void;
  loading?: boolean;
}

export function PropertyFilters({ value, onChange, onSearch, loading }: PropertyFiltersProps) {
  const { propertyTypes, statuses } = useLookups();

  const updateFilter = (patch: Partial<PropertySearchRequest["filters"]>) => {
    onChange({
      ...value,
      filters: { ...(value.filters || {}), ...patch },
    });
  };

  const clearFilters = () => {
    onChange({ query: "", filters: {}, geo: undefined, sort: value.sort });
  };

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="sticky top-[76px] z-30 rounded-3xl border border-border/80 glass-strong p-5 shadow-soft"
    >
      <div className="mb-4 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-accent text-primary">
            <SlidersHorizontal className="h-4 w-4" strokeWidth={1.75} />
          </div>
          <div>
            <p className="text-[13px] font-semibold tracking-tight">{brand.name} filters</p>
            <p className="text-[11px] text-muted-foreground">Refine your portfolio view</p>
          </div>
        </div>
        <BrandLogo size="xs" href={null} className="opacity-80" />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-1.5">
          <Label htmlFor="query" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Search
          </Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              id="query"
              placeholder="Title, code, address…"
              className="h-11 rounded-xl border-border bg-white pl-9"
              value={value.query || ""}
              onChange={(e) => onChange({ ...value, query: e.target.value })}
              onKeyDown={(e) => e.key === "Enter" && onSearch()}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <Label className="text-[11px] uppercase tracking-wide text-muted-foreground">Type</Label>
          <Select
            value={value.filters?.property_types?.[0] || "_all"}
            onValueChange={(v) =>
              updateFilter({ property_types: v === "_all" ? undefined : [v as never] })
            }
          >
            <SelectTrigger className="h-11 rounded-xl bg-white">
              <SelectValue placeholder="All types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">All types</SelectItem>
              {propertyTypes.map((t) => (
                <SelectItem key={t.code} value={t.code}>
                  {t.code}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label className="text-[11px] uppercase tracking-wide text-muted-foreground">Status</Label>
          <Select
            value={value.filters?.status?.[0] || "_all"}
            onValueChange={(v) =>
              updateFilter({ status: v === "_all" ? undefined : [v as never] })
            }
          >
            <SelectTrigger className="h-11 rounded-xl bg-white">
              <SelectValue placeholder="All statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="_all">All statuses</SelectItem>
              {statuses.map((s) => (
                <SelectItem key={s.code} value={s.code}>
                  {s.code}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="province" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Province
          </Label>
          <Input
            id="province"
            placeholder="e.g. İstanbul"
            className="h-11 rounded-xl bg-white"
            value={value.filters?.provinces?.[0] || ""}
            onChange={(e) =>
              updateFilter({ provinces: e.target.value ? [e.target.value] : undefined })
            }
            onKeyDown={(e) => e.key === "Enter" && onSearch()}
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="min-price" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Min price
          </Label>
          <Input
            id="min-price"
            type="number"
            placeholder="0"
            className="h-11 rounded-xl bg-white"
            value={value.filters?.sale_price?.min ?? ""}
            onChange={(e) =>
              updateFilter({
                sale_price: {
                  ...value.filters?.sale_price,
                  min: e.target.value ? Number(e.target.value) : undefined,
                },
              })
            }
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="max-price" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Max price
          </Label>
          <Input
            id="max-price"
            type="number"
            placeholder="Any"
            className="h-11 rounded-xl bg-white"
            value={value.filters?.sale_price?.max ?? ""}
            onChange={(e) =>
              updateFilter({
                sale_price: {
                  ...value.filters?.sale_price,
                  max: e.target.value ? Number(e.target.value) : undefined,
                },
              })
            }
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="min-area" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Min area (m²)
          </Label>
          <Input
            id="min-area"
            type="number"
            placeholder="0"
            className="h-11 rounded-xl bg-white"
            value={value.filters?.net_area_sqm?.min ?? ""}
            onChange={(e) =>
              updateFilter({
                net_area_sqm: {
                  ...value.filters?.net_area_sqm,
                  min: e.target.value ? Number(e.target.value) : undefined,
                },
              })
            }
          />
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="max-area" className="text-[11px] uppercase tracking-wide text-muted-foreground">
            Max area (m²)
          </Label>
          <Input
            id="max-area"
            type="number"
            placeholder="Any"
            className="h-11 rounded-xl bg-white"
            value={value.filters?.net_area_sqm?.max ?? ""}
            onChange={(e) =>
              updateFilter({
                net_area_sqm: {
                  ...value.filters?.net_area_sqm,
                  max: e.target.value ? Number(e.target.value) : undefined,
                },
              })
            }
          />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        <Button
          onClick={onSearch}
          disabled={loading}
          className="h-11 rounded-2xl px-5 shadow-glow"
        >
          <Search className="mr-2 h-4 w-4" />
          Apply filters
        </Button>
        <Button
          variant="outline"
          onClick={clearFilters}
          disabled={loading}
          className="h-11 rounded-2xl"
        >
          <X className="mr-2 h-4 w-4" />
          Clear
        </Button>
      </div>
    </MotionDiv>
  );
}
