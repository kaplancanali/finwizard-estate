"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui-custom/page-header";
import { PropertyFilters } from "@/components/properties/property-filters";
import { PropertyCard } from "@/components/properties/property-card";
import { EmptyState } from "@/components/ui-custom/empty-state";
import { useProperties } from "@/hooks/useProperties";
import { PropertySearchRequest } from "@/lib/types/api";
import { CardSkeleton } from "@/components/ui-custom/skeleton";

export default function PropertySearchPage() {
  const [criteria, setCriteria] = useState<PropertySearchRequest>({
    query: "",
    filters: {},
  });

  const { items, loading, error, search } = useProperties({ autoFetch: false });
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = () => {
    setHasSearched(true);
    search(criteria);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Discover"
        title="Advanced search"
        description="Query the full Torkam asset universe with institutional filters."
        action={
          <Button onClick={handleSearch} disabled={loading} className="h-11 rounded-2xl px-5 shadow-glow">
            <Search className="mr-2 h-4 w-4" />
            Run search
          </Button>
        }
      />

      <PropertyFilters value={criteria} onChange={setCriteria} onSearch={handleSearch} loading={loading} />

      {!hasSearched ? (
        <EmptyState
          title="Ready when you are"
          description="Set filters above and run a search across title, location, price and typology."
        />
      ) : loading ? (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      ) : error ? (
        <EmptyState title="Search failed" description={error} />
      ) : items.length === 0 ? (
        <EmptyState title="No results" description="Try broadening filters or clearing constraints." />
      ) : (
        <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {items.map((property, i) => (
            <PropertyCard key={property.id} property={property} index={i} />
          ))}
        </div>
      )}
    </div>
  );
}
