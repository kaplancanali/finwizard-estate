"use client";

import { useState } from "react";
import Link from "next/link";
import { Plus, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useProperties } from "@/hooks/useProperties";
import { PropertySearchRequest } from "@/lib/types/api";
import { PropertyFilters } from "./property-filters";
import { PropertyCard } from "./property-card";
import { EmptyState, EmptyStateCTA } from "../ui-custom/empty-state";
import { PageHeader } from "../ui-custom/page-header";
import { CardSkeleton } from "../ui-custom/skeleton";
import { useAuth } from "@/components/auth/auth-provider";

export function PropertyList() {
  const { can } = useAuth();
  const [criteria, setCriteria] = useState<PropertySearchRequest>({
    query: "",
    filters: {},
    sort: [{ field: "created_at", direction: "desc" }],
  });

  const { items, pagination, loading, error, search } = useProperties({ autoFetch: true });

  const handleSearch = () => search(criteria);
  const handlePageChange = (page: number) => {
    if (!pagination) return;
    search({ ...criteria, pagination: { page, page_size: pagination.page_size } });
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Portfolio"
        title="Property holdings"
        description="Browse, filter and operate every asset in the Torkam book."
        action={
          can("property:create") ? (
            <Button asChild className="h-11 rounded-2xl px-5 shadow-glow">
              <Link href="/properties/new">
                <Plus className="mr-2 h-4 w-4" />
                New asset
              </Link>
            </Button>
          ) : undefined
        }
      />

      <PropertyFilters value={criteria} onChange={setCriteria} onSearch={handleSearch} loading={loading} />

      {loading ? (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <EmptyState
          title="Could not load portfolio"
          description={error}
          action={<EmptyStateCTA href="/properties" label="Retry" />}
        />
      ) : items.length === 0 ? (
        <EmptyState
          title="No properties found"
          description="Adjust filters or register the first asset in your portfolio."
          action={<EmptyStateCTA href="/properties/new" label="Create property" />}
          secondaryAction={<EmptyStateCTA href="/properties/search" label="Advanced search" variant="outline" />}
        />
      ) : (
        <>
          <div className="flex items-center justify-between text-[12px] text-muted-foreground">
            <span>
              Showing <strong className="text-foreground">{items.length}</strong>
              {pagination ? ` of ${pagination.total_items}` : ""} assets
            </span>
          </div>
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {items.map((property, i) => (
              <PropertyCard key={property.id} property={property} index={i} />
            ))}
          </div>

          {pagination && pagination.total_pages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-2">
              <Button
                variant="outline"
                size="sm"
                className="h-10 w-10 rounded-xl p-0"
                disabled={!pagination.has_previous}
                onClick={() => handlePageChange(pagination.page - 1)}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="min-w-24 text-center text-[13px] text-muted-foreground">
                {pagination.page} / {pagination.total_pages}
              </span>
              <Button
                variant="outline"
                size="sm"
                className="h-10 w-10 rounded-xl p-0"
                disabled={!pagination.has_next}
                onClick={() => handlePageChange(pagination.page + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
