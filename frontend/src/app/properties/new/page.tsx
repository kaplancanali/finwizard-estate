import { PageHeader } from "@/components/ui-custom/page-header";
import { PropertyForm } from "@/components/properties/property-form";

export default function NewPropertyPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Create"
        title="Register new asset"
        description="Capture title, pricing, location and building attributes into the Torkam ledger."
      />
      <div className="rounded-3xl border border-border/80 bg-white p-5 shadow-soft sm:p-8">
        <PropertyForm mode="create" />
      </div>
    </div>
  );
}
