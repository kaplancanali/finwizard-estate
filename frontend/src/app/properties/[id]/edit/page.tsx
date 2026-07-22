"use client";

import { useEffect, useState } from "react";
import { PageHeader } from "@/components/ui-custom/page-header";
import { PropertyForm } from "@/components/properties/property-form";
import { useProperty } from "@/hooks/useProperties";
import { DashboardSkeleton } from "@/components/ui-custom/skeleton";

interface EditPropertyPageProps {
  params: Promise<{ id: string }>;
}

export default function EditPropertyPage({ params }: EditPropertyPageProps) {
  const [id, setId] = useState<string | null>(null);

  useEffect(() => {
    params.then((p) => setId(p.id));
  }, [params]);

  if (!id) return <DashboardSkeleton />;
  return <EditPropertyForm id={id} />;
}

function EditPropertyForm({ id }: { id: string }) {
  const { property, loading } = useProperty(id, "images");

  if (loading || !property) {
    return (
      <div className="space-y-6">
        <PageHeader eyebrow="Edit" title="Edit asset" description="Loading dossier…" />
        <DashboardSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Edit"
        title="Edit asset"
        description={`${property.title} · ${property.property_code}`}
      />
      <div className="rounded-3xl border border-border/80 bg-white p-5 shadow-soft sm:p-8">
        <PropertyForm property={property} mode="edit" />
      </div>
    </div>
  );
}
