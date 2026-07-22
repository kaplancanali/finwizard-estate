"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useLookups, usePropertyMutations } from "@/hooks/useProperties";
import { Property, PropertyCreateRequest, PropertyUpdateRequest } from "@/lib/types/api";

interface PropertyFormProps {
  property?: Property;
  mode: "create" | "edit";
}

function buildPricing(pricing?: Partial<Property["pricing"]> | null): PropertyCreateRequest["pricing"] {
  return {
    sale_price: pricing?.sale_price ?? null,
    rental_price: pricing?.rental_price ?? null,
    maintenance_fee: pricing?.maintenance_fee ?? null,
    currency: pricing?.currency || "TRY",
    price_on_request: pricing?.price_on_request ?? false,
  };
}

const emptyLocation: PropertyCreateRequest["location"] = {
  country_code: "TR",
  province: "",
  district: "",
  neighborhood: "",
  street: "",
  postal_code: "",
  address_line: "",
  latitude: undefined as unknown as string | undefined,
  longitude: undefined as unknown as string | undefined,
};

const emptyBuilding: PropertyCreateRequest["building"] = {
  construction_year: undefined,
  floor_count: undefined,
  floor_number: undefined,
  unit_number: "",
  net_area_sqm: undefined as unknown as string | undefined,
  gross_area_sqm: undefined as unknown as string | undefined,
  room_count: undefined as unknown as string | undefined,
  living_room_count: undefined,
  bedroom_count: undefined,
  bathroom_count: undefined,
  balcony_count: undefined,
  parking_count: undefined,
};

const emptyFeatures: PropertyCreateRequest["features"] = {
  heating_type: "",
  cooling_type: "",
  energy_certificate_class: "",
  has_elevator: false,
  has_parking: false,
  has_balcony: false,
  has_garden: false,
  has_pool: false,
  has_security: false,
  has_storage: false,
  has_smart_home: false,
  has_solar: false,
  has_ev_charger: false,
  accessibility_level: "",
};

export function PropertyForm({ property, mode }: PropertyFormProps) {
  const router = useRouter();
  const { propertyTypes, statuses } = useLookups();
  const { create, update } = usePropertyMutations();

  const [form, setForm] = useState<PropertyCreateRequest>({
    title: property?.title || "",
    description: property?.description || "",
    property_type: property?.property_type || "apartment",
    property_category: property?.property_category || "residential",
    property_subtype: property?.property_subtype || "",
    status: property?.status || "draft",
    visibility: property?.visibility || "private",
    pricing: buildPricing(property?.pricing),
    location: property?.location || { ...emptyLocation },
    parcel: property?.parcel || null,
    building: property?.building || { ...emptyBuilding },
    features: property?.features || { ...emptyFeatures },
    amenities: property?.amenities || [],
    tags: property?.tags || [],
  });

  const [amenityInput, setAmenityInput] = useState("");
  const [tagInput, setTagInput] = useState("");

  const updateField = <K extends keyof PropertyCreateRequest>(key: K, value: PropertyCreateRequest[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const addAmenity = () => {
    if (!amenityInput.trim()) return;
    setForm((prev) => ({ ...prev, amenities: [...prev.amenities, amenityInput.trim()] }));
    setAmenityInput("");
  };

  const removeAmenity = (index: number) => {
    setForm((prev) => ({
      ...prev,
      amenities: prev.amenities.filter((_, i) => i !== index),
    }));
  };

  const addTag = () => {
    if (!tagInput.trim()) return;
    setForm((prev) => ({ ...prev, tags: [...prev.tags, tagInput.trim()] }));
    setTagInput("");
  };

  const removeTag = (index: number) => {
    setForm((prev) => ({ ...prev, tags: prev.tags.filter((_, i) => i !== index) }));
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (mode === "create") {
        const created = await create(form);
        toast.success("Property created", { description: created.property_code });
        router.push(`/properties/${created.id}`);
      } else if (property) {
        const patch: PropertyUpdateRequest = {
          version: property.version,
          title: form.title,
          description: form.description,
          pricing: form.pricing || null,
          location: form.location || null,
          parcel: form.parcel || null,
          building: form.building || null,
          features: form.features || null,
          amenities: form.amenities,
          tags: form.tags,
        };
        await update(property.id, patch);
        toast.success("Property updated");
        router.push(`/properties/${property.id}`);
      }
    } catch {
      // errors already toasted
    }
  };

  return (
    <form onSubmit={onSubmit} className="space-y-6">
      <Tabs defaultValue="basic" className="w-full">
        <TabsList className="mb-4 h-11 rounded-2xl bg-secondary p-1">
          <TabsTrigger value="basic" className="rounded-xl">Basic</TabsTrigger>
          <TabsTrigger value="location" className="rounded-xl">Location</TabsTrigger>
          <TabsTrigger value="building" className="rounded-xl">Building</TabsTrigger>
          <TabsTrigger value="features" className="rounded-xl">Features</TabsTrigger>
          <TabsTrigger value="media" className="rounded-xl">Media & Tags</TabsTrigger>
        </TabsList>

        <TabsContent value="basic" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Basic Information</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  required
                  value={form.title}
                  onChange={(e) => updateField("title", e.target.value)}
                />
              </div>
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  rows={4}
                  value={form.description || ""}
                  onChange={(e) => updateField("description", e.target.value || null)}
                />
              </div>
              <div className="space-y-1">
                <Label>Type</Label>
                <Select
                  value={form.property_type}
                  onValueChange={(v) => updateField("property_type", v as never)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {propertyTypes.map((t) => (
                      <SelectItem key={t.code} value={t.code}>
                        {t.code}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Category</Label>
                <Select
                  value={form.property_category}
                  onValueChange={(v) => updateField("property_category", v as never)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="residential">Residential</SelectItem>
                    <SelectItem value="commercial">Commercial</SelectItem>
                    <SelectItem value="land">Land</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label>Status</Label>
                <Select
                  value={form.status}
                  onValueChange={(v) => updateField("status", v as never)}
                >
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
              <div className="space-y-1">
                <Label>Visibility</Label>
                <Select
                  value={form.visibility}
                  onValueChange={(v) => updateField("visibility", v as never)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="private">Private</SelectItem>
                    <SelectItem value="public">Public</SelectItem>
                    <SelectItem value="restricted">Restricted</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Pricing</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-1">
                <Label htmlFor="sale-price">Sale Price</Label>
                <Input
                  id="sale-price"
                  type="number"
                  step="0.01"
                  value={form.pricing?.sale_price || ""}
                  onChange={(e) =>
                    updateField(
                      "pricing",
                      buildPricing({ ...form.pricing, sale_price: e.target.value ? e.target.value : null })
                    )
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="rental-price">Rental Price</Label>
                <Input
                  id="rental-price"
                  type="number"
                  step="0.01"
                  value={form.pricing?.rental_price || ""}
                  onChange={(e) =>
                    updateField(
                      "pricing",
                      buildPricing({ ...form.pricing, rental_price: e.target.value ? e.target.value : null })
                    )
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="currency">Currency</Label>
                <Input
                  id="currency"
                  maxLength={3}
                  value={form.pricing?.currency || "TRY"}
                  onChange={(e) =>
                    updateField(
                      "pricing",
                      buildPricing({ ...form.pricing, currency: e.target.value.toUpperCase() })
                    )
                  }
                />
              </div>
              <div className="flex items-center gap-2 sm:col-span-3">
                <Switch
                  id="price-on-request"
                  checked={form.pricing?.price_on_request || false}
                  onCheckedChange={(checked) =>
                    updateField("pricing", buildPricing({ ...form.pricing, price_on_request: checked }))
                  }
                />
                <Label htmlFor="price-on-request">Price on request</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="location" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Location</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-1">
                <Label htmlFor="country">Country Code</Label>
                <Input
                  id="country"
                  maxLength={2}
                  value={form.location?.country_code || ""}
                  onChange={(e) =>
                    updateField("location", {
                      ...form.location,
                      country_code: e.target.value.toUpperCase(),
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="province">Province</Label>
                <Input
                  id="province"
                  value={form.location?.province || ""}
                  onChange={(e) =>
                    updateField("location", { ...form.location, province: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="district">District</Label>
                <Input
                  id="district"
                  value={form.location?.district || ""}
                  onChange={(e) =>
                    updateField("location", { ...form.location, district: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="neighborhood">Neighborhood</Label>
                <Input
                  id="neighborhood"
                  value={form.location?.neighborhood || ""}
                  onChange={(e) =>
                    updateField("location", { ...form.location, neighborhood: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1 sm:col-span-2">
                <Label htmlFor="address">Address Line</Label>
                <Textarea
                  id="address"
                  value={form.location?.address_line || ""}
                  onChange={(e) =>
                    updateField("location", { ...form.location, address_line: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="latitude">Latitude</Label>
                <Input
                  id="latitude"
                  type="number"
                  step="any"
                  value={form.location?.latitude || ""}
                  onChange={(e) =>
                    updateField("location", {
                      ...form.location,
                      latitude: e.target.value ? e.target.value : null,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="longitude">Longitude</Label>
                <Input
                  id="longitude"
                  type="number"
                  step="any"
                  value={form.location?.longitude || ""}
                  onChange={(e) =>
                    updateField("location", {
                      ...form.location,
                      longitude: e.target.value ? e.target.value : null,
                    })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="building" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Building Details</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-3">
              <div className="space-y-1">
                <Label htmlFor="construction-year">Construction Year</Label>
                <Input
                  id="construction-year"
                  type="number"
                  value={form.building?.construction_year || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      construction_year: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="floor-count">Floor Count</Label>
                <Input
                  id="floor-count"
                  type="number"
                  value={form.building?.floor_count || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      floor_count: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="floor-number">Floor Number</Label>
                <Input
                  id="floor-number"
                  type="number"
                  value={form.building?.floor_number || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      floor_number: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="net-area">Net Area (m²)</Label>
                <Input
                  id="net-area"
                  type="number"
                  step="0.01"
                  value={form.building?.net_area_sqm || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      net_area_sqm: e.target.value ? e.target.value : null,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="gross-area">Gross Area (m²)</Label>
                <Input
                  id="gross-area"
                  type="number"
                  step="0.01"
                  value={form.building?.gross_area_sqm || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      gross_area_sqm: e.target.value ? e.target.value : null,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="rooms">Rooms</Label>
                <Input
                  id="rooms"
                  type="number"
                  step="0.5"
                  value={form.building?.room_count || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      room_count: e.target.value ? e.target.value : null,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="bedrooms">Bedrooms</Label>
                <Input
                  id="bedrooms"
                  type="number"
                  value={form.building?.bedroom_count || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      bedroom_count: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="bathrooms">Bathrooms</Label>
                <Input
                  id="bathrooms"
                  type="number"
                  value={form.building?.bathroom_count || ""}
                  onChange={(e) =>
                    updateField("building", {
                      ...form.building,
                      bathroom_count: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="unit-number">Unit Number</Label>
                <Input
                  id="unit-number"
                  value={form.building?.unit_number || ""}
                  onChange={(e) =>
                    updateField("building", { ...form.building, unit_number: e.target.value })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="features" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Features</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-1">
                <Label htmlFor="heating">Heating</Label>
                <Input
                  id="heating"
                  value={form.features?.heating_type || ""}
                  onChange={(e) =>
                    updateField("features", { ...form.features, heating_type: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="cooling">Cooling</Label>
                <Input
                  id="cooling"
                  value={form.features?.cooling_type || ""}
                  onChange={(e) =>
                    updateField("features", { ...form.features, cooling_type: e.target.value })
                  }
                />
              </div>
              <div className="space-y-1">
                <Label htmlFor="energy">Energy Class</Label>
                <Input
                  id="energy"
                  maxLength={1}
                  value={form.features?.energy_certificate_class || ""}
                  onChange={(e) =>
                    updateField("features", {
                      ...form.features,
                      energy_certificate_class: e.target.value.toUpperCase(),
                    })
                  }
                />
              </div>
              {(
                [
                  "has_elevator",
                  "has_parking",
                  "has_balcony",
                  "has_garden",
                  "has_pool",
                  "has_security",
                  "has_storage",
                  "has_smart_home",
                  "has_solar",
                  "has_ev_charger",
                ] as const
              ).map((key) => (
                <div key={key} className="flex items-center gap-2">
                  <Switch
                    id={key}
                    checked={(form.features?.[key] as boolean) || false}
                    onCheckedChange={(checked) =>
                      updateField("features", { ...form.features, [key]: checked })
                    }
                  />
                  <Label htmlFor={key} className="capitalize">
                    {key.replace("has_", "").replace("_", " ")}
                  </Label>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="media" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tags & Amenities</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1">
                <Label htmlFor="amenities">Amenities</Label>
                <div className="flex gap-2">
                  <Input
                    id="amenities"
                    value={amenityInput}
                    onChange={(e) => setAmenityInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addAmenity())}
                    placeholder="e.g. pool, gym, parking"
                  />
                  <Button type="button" variant="outline" onClick={addAmenity}>
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {form.amenities.map((amenity, i) => (
                    <span
                      key={`${amenity}-${i}`}
                      className="inline-flex items-center gap-1 rounded-full bg-secondary px-3 py-1 text-xs"
                    >
                      {amenity}
                      <button type="button" onClick={() => removeAmenity(i)} className="text-muted-foreground hover:text-foreground">
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="space-y-1">
                <Label htmlFor="tags">Tags</Label>
                <div className="flex gap-2">
                  <Input
                    id="tags"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addTag())}
                    placeholder="e.g. sea-view, new-building"
                  />
                  <Button type="button" variant="outline" onClick={addTag}>
                    Add
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2 mt-2">
                  {form.tags.map((tag, i) => (
                    <span
                      key={`${tag}-${i}`}
                      className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-xs text-primary"
                    >
                      {tag}
                      <button type="button" onClick={() => removeTag(i)} className="hover:text-foreground">
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <div className="flex items-center justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={() => router.back()} className="h-11 rounded-2xl">
          Cancel
        </Button>
        <Button type="submit" className="h-11 rounded-2xl px-6 shadow-glow">
          {mode === "create" ? "Create property" : "Save changes"}
        </Button>
      </div>
    </form>
  );
}
