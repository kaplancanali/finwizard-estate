"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  MapPin,
  Calendar,
  Hash,
  Tag,
  Edit,
  Trash2,
  RefreshCcw,
  ArrowLeft,
  DollarSign,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLookups, useProperty } from "@/hooks/useProperties";
import { usePropertyMutations } from "@/hooks/useProperties";
import { PropertyStatusBadge } from "./property-status-badge";
import { PropertyStatus, StatusHistoryItem } from "@/lib/types/api";
import { formatDate, formatPrice } from "@/lib/api/client";
import { MotionDiv } from "@/lib/motion";
import { DashboardSkeleton } from "@/components/ui-custom/skeleton";
import { BrandLogo } from "@/components/ui-custom/brand-logo";
import { brand } from "@/lib/design-system";
import { AnalysisPanel } from "@/components/properties/analysis-panel";

interface PropertyDetailProps {
  id: string;
}

export function PropertyDetail({ id }: PropertyDetailProps) {
  const router = useRouter();
  const { property, loading, refresh } = useProperty(id, "images,documents,history");
  const { changeStatus, remove, restore } = usePropertyMutations();
  const { statuses } = useLookups();
  const [newStatus, setNewStatus] = useState<PropertyStatus>("draft");
  const [openDelete, setOpenDelete] = useState(false);
  const [openStatus, setOpenStatus] = useState(false);

  if (loading || !property) {
    return <DashboardSkeleton />;
  }

  const handleDelete = async () => {
    try {
      await remove(id);
      toast.success("Property deleted");
      router.push("/properties");
    } catch {
      // already toasted
    } finally {
      setOpenDelete(false);
    }
  };

  const handleRestore = async () => {
    try {
      await restore(id);
      toast.success("Property restored");
      refresh();
    } catch {
      // already toasted
    }
  };

  const handleStatusChange = async () => {
    try {
      await changeStatus(id, { version: property.version, status: newStatus });
      toast.success("Status updated");
      setOpenStatus(false);
      refresh();
    } catch {
      // already toasted
    }
  };

  const price = property.pricing?.sale_price || property.pricing?.rental_price;

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="space-y-6"
    >
      <div className="flex items-center justify-between">
        <Button variant="outline" asChild className="h-10 rounded-xl">
          <Link href="/properties">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to portfolio
          </Link>
        </Button>
        <div className="flex items-center gap-2">
          <Button variant="outline" asChild className="h-10 rounded-xl">
            <Link href={`/properties/${id}/edit`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          {property.status === "deleted" ? (
            <Button variant="outline" onClick={handleRestore}>
              <RefreshCcw className="mr-2 h-4 w-4" />
              Restore
            </Button>
          ) : (
            <Dialog open={openDelete} onOpenChange={setOpenDelete}>
              <DialogTrigger asChild>
                <Button variant="destructive">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Delete Property</DialogTitle>
                  <DialogDescription>
                    This will soft-delete the property. It can be restored later.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setOpenDelete(false)}>
                    Cancel
                  </Button>
                  <Button variant="destructive" onClick={handleDelete}>
                    Delete
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          <div>
            <div className="flex items-center gap-2">
              <BrandLogo size="xs" href={null} className="opacity-90" />
              <PropertyStatusBadge status={property.status} />
              <span className="text-xs text-muted-foreground">{property.property_type}</span>
              <span className="text-xs text-muted-foreground">·</span>
              <span className="text-xs text-muted-foreground">{property.property_category}</span>
            </div>
            <h1 className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight sm:text-4xl">
              {property.title}
            </h1>
            <p className="mt-1 flex items-center gap-1 text-muted-foreground">
              <MapPin className="h-4 w-4" />
              {[property.location.province, property.location.district, property.location.neighborhood]
                .filter(Boolean)
                .join(", ")}
            </p>
          </div>

          {property.images && property.images.length > 0 ? (
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {property.images.map((img) => (
                <div key={img.id} className="relative aspect-video overflow-hidden rounded-lg bg-muted">
                  {img.url ? (
                    <Image src={img.url} alt={img.caption || "Property image"} fill className="object-cover" />
                  ) : (
                    <div className="flex h-full items-center justify-center text-muted-foreground">No image</div>
                  )}
                  {img.is_primary && (
                    <Badge className="absolute left-2 top-2" variant="default">
                      Primary
                    </Badge>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center rounded-lg border border-dashed text-muted-foreground">
              No images yet
            </div>
          )}

          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="analysis">Analysis</TabsTrigger>
              <TabsTrigger value="building">Building</TabsTrigger>
              <TabsTrigger value="features">Features</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>
            <TabsContent value="overview" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Description</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="whitespace-pre-wrap text-sm leading-relaxed">
                    {property.description || "No description provided."}
                  </p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Location Details</CardTitle>
                </CardHeader>
                <CardContent className="grid gap-2 text-sm sm:grid-cols-2">
                  <Detail label="Country" value={property.location.country_code} />
                  <Detail label="Province" value={property.location.province} />
                  <Detail label="District" value={property.location.district} />
                  <Detail label="Neighborhood" value={property.location.neighborhood} />
                  <Detail label="Street" value={property.location.street} />
                  <Detail label="Postal Code" value={property.location.postal_code} />
                  <Detail label="Address" value={property.location.address_line} />
                  <Detail label="Coordinates" value={`${property.location.latitude}, ${property.location.longitude}`} />
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="analysis" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Market & risk analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <AnalysisPanel property={property} />
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="building" className="space-y-4">
              <Card>
                <CardContent className="grid gap-2 pt-6 text-sm sm:grid-cols-2 lg:grid-cols-3">
                  <Detail label="Construction Year" value={property.building?.construction_year} />
                  <Detail label="Floor Count" value={property.building?.floor_count} />
                  <Detail label="Floor Number" value={property.building?.floor_number} />
                  <Detail label="Unit Number" value={property.building?.unit_number} />
                  <Detail label="Net Area" value={property.building?.net_area_sqm ? `${property.building.net_area_sqm} m²` : undefined} />
                  <Detail label="Gross Area" value={property.building?.gross_area_sqm ? `${property.building.gross_area_sqm} m²` : undefined} />
                  <Detail label="Rooms" value={property.building?.room_count} />
                  <Detail label="Bedrooms" value={property.building?.bedroom_count} />
                  <Detail label="Bathrooms" value={property.building?.bathroom_count} />
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="features" className="space-y-4">
              <Card>
                <CardContent className="pt-6">
                  {property.features ? (
                    <div className="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-3">
                      <Detail label="Heating" value={property.features.heating_type} />
                      <Detail label="Cooling" value={property.features.cooling_type} />
                      <Detail label="Energy Class" value={property.features.energy_certificate_class} />
                      <FeatureFlag label="Elevator" value={property.features.has_elevator} />
                      <FeatureFlag label="Parking" value={property.features.has_parking} />
                      <FeatureFlag label="Balcony" value={property.features.has_balcony} />
                      <FeatureFlag label="Garden" value={property.features.has_garden} />
                      <FeatureFlag label="Pool" value={property.features.has_pool} />
                      <FeatureFlag label="Security" value={property.features.has_security} />
                      <FeatureFlag label="Storage" value={property.features.has_storage} />
                      <FeatureFlag label="Smart Home" value={property.features.has_smart_home} />
                      <FeatureFlag label="Solar" value={property.features.has_solar} />
                      <FeatureFlag label="EV Charger" value={property.features.has_ev_charger} />
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No features recorded.</p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
            <TabsContent value="history" className="space-y-4">
              <StatusHistory propertyId={id} />
            </TabsContent>
          </Tabs>
        </div>

        <div className="space-y-4">
          <Card className="rounded-3xl border-border/80 shadow-soft">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-base font-[family-name:var(--font-display)]">Pricing</CardTitle>
              <BrandLogo size="xs" href={null} className="opacity-70" />
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-2xl font-bold">
                <DollarSign className="h-5 w-5" />
                {formatPrice(price, property.pricing?.currency)}
                {property.pricing?.price_on_request && <Badge variant="outline">On Request</Badge>}
              </div>
              <Separator />
              <div className="grid gap-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Sale</span>
                  <span>{formatPrice(property.pricing?.sale_price, property.pricing?.currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rent</span>
                  <span>{formatPrice(property.pricing?.rental_price, property.pricing?.currency)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Maintenance</span>
                  <span>{formatPrice(property.pricing?.maintenance_fee, property.pricing?.currency)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Dialog open={openStatus} onOpenChange={setOpenStatus}>
                <DialogTrigger asChild>
                  <Button className="w-full" variant="outline">
                    Change Status
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Change Status</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-4 py-2">
                    <Select value={newStatus} onValueChange={(v) => setNewStatus(v as PropertyStatus)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {statuses.map((s) => (
                          <SelectItem key={s.code} value={s.code}>
                            {s.code}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setOpenStatus(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleStatusChange}>Update Status</Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Hash className="h-4 w-4" />
                {property.property_code}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Tag className="h-4 w-4" />
                {property.slug}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                Created {formatDate(property.created_at)}
              </div>
              <div className="flex items-center gap-2 text-muted-foreground">
                <Calendar className="h-4 w-4" />
                Updated {formatDate(property.updated_at)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tags</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {property.tags.length > 0 ? (
                  property.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">
                      {tag}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-muted-foreground">No tags</span>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </MotionDiv>
  );
}

function Detail({ label, value }: { label: string; value?: React.ReactNode }) {
  if (value === undefined || value === null || value === "") return null;
  return (
    <div>
      <span className="block text-xs font-medium text-muted-foreground">{label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

function FeatureFlag({ label, value }: { label: string; value?: boolean }) {
  return (
    <div className="flex items-center gap-2">
      <span className={value ? "text-green-600" : "text-muted-foreground"}>●</span>
      <span className={value ? "font-medium" : "text-muted-foreground"}>{label}</span>
    </div>
  );
}

function StatusHistory({ propertyId }: { propertyId: string }) {
  const [items, setItems] = useState<StatusHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    import("@/lib/api/properties")
      .then((api) => api.getStatusHistory(propertyId))
      .then((res) => {
        if (!cancelled) setItems(res.data);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [propertyId]);

  if (loading) return <div className="h-32 animate-pulse rounded bg-muted" />;
  if (items.length === 0) return <p className="text-sm text-muted-foreground">No status history yet.</p>;

  return (
    <div className="space-y-2">
      {items.map((item) => (
        <div key={item.id} className="rounded-lg border p-3 text-sm">
          <div className="flex items-center gap-2">
            <PropertyStatusBadge status={item.old_status || "unknown"} />
            <span>→</span>
            <PropertyStatusBadge status={item.new_status || "unknown"} />
          </div>
          <p className="mt-1 text-xs text-muted-foreground">Reason: {item.reason || "—"}</p>
        </div>
      ))}
    </div>
  );
}
