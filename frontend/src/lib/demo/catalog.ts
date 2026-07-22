/**
 * In-memory demo catalog for Vercel when BACKEND_URL is unset / localhost.
 * Shapes match property-service API responses used by the UI.
 */

export type DemoProperty = {
  id: string;
  tenant_id: string;
  property_code: string;
  slug: string;
  title: string;
  description: string;
  property_type: string;
  property_category: string;
  status: string;
  visibility: string;
  version: number;
  pricing: {
    sale_price: string | null;
    rental_price: string | null;
    currency: string;
    price_on_request: boolean;
  };
  location: {
    country_code: string;
    province: string;
    district: string | null;
    neighborhood: string | null;
    street: string | null;
    latitude: string | null;
    longitude: string | null;
  };
  building: Record<string, unknown> | null;
  features: Record<string, unknown> | null;
  amenities: string[];
  tags: string[];
  images: Array<{
    id: string;
    url: string;
    is_primary: boolean;
    sort_order: number;
    caption: string | null;
  }>;
  created_at: string;
  updated_at: string;
};

const TENANT = "00000000-0000-0000-0000-000000000010";
const NOW = "2026-07-22T12:00:00Z";

const IMG = {
  residence: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
  apartment: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
  villa: "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1200&q=80",
  office: "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80",
  land: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=80",
  store: "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80",
};

function prop(
  partial: Omit<
    DemoProperty,
    "tenant_id" | "visibility" | "version" | "created_at" | "updated_at" | "amenities" | "tags" | "images"
  > & {
    amenities?: string[];
    tags?: string[];
    image: string;
  }
): DemoProperty {
  const { image, amenities, tags, ...rest } = partial;
  return {
    ...rest,
    tenant_id: TENANT,
    visibility: "tenant",
    version: 1,
    created_at: NOW,
    updated_at: NOW,
    amenities: amenities || [],
    tags: tags || ["demo-seed"],
    images: [
      {
        id: `${rest.id}-img`,
        url: image,
        is_primary: true,
        sort_order: 0,
        caption: rest.title,
      },
    ],
  };
}

export const DEMO_PROPERTIES: DemoProperty[] = [
  prop({
    id: "11111111-1111-1111-1111-111111111101",
    property_code: "FW-TR-BESIKT-00000001",
    slug: "besiktas-bogaz-manzarali-residence",
    title: "Beşiktaş Boğaz Manzaralı Residence",
    description: "Torkam portföyü — deniz manzaralı 3+1 residence.",
    property_type: "residence",
    property_category: "residential",
    status: "active",
    pricing: { sale_price: "18500000.00", rental_price: null, currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "İstanbul",
      district: "Beşiktaş",
      neighborhood: "Levent",
      street: "Büyükdere Cad.",
      latitude: "41.081200",
      longitude: "29.012300",
    },
    building: { net_area_sqm: "165.00", room_count: "3.5", bedroom_count: 3, bathroom_count: 2 },
    features: { has_elevator: true, has_parking: true, has_security: true },
    amenities: ["parking", "security", "elevator", "gym"],
    tags: ["demo-seed", "istanbul"],
    image: IMG.residence,
  }),
  prop({
    id: "11111111-1111-1111-1111-111111111102",
    property_code: "FW-TR-KADIKY-00000001",
    slug: "kadikoy-moda-terasli-daire",
    title: "Kadıköy Moda Teraslı Daire",
    description: "Moda'ya yakın teraslı 2+1 daire.",
    property_type: "apartment",
    property_category: "residential",
    status: "active",
    pricing: { sale_price: "9200000.00", rental_price: "65000.00", currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "İstanbul",
      district: "Kadıköy",
      neighborhood: "Moda",
      street: null,
      latitude: "40.984500",
      longitude: "29.025100",
    },
    building: { net_area_sqm: "98.00", room_count: "2.5", bedroom_count: 2, bathroom_count: 1 },
    features: { has_elevator: true, has_balcony: true },
    image: IMG.apartment,
  }),
  prop({
    id: "11111111-1111-1111-1111-111111111103",
    property_code: "FW-TR-CANKAY-00000001",
    slug: "cankaya-villa-bahceli",
    title: "Çankaya Villa — Bahçeli",
    description: "Ankara Çankaya'da bahçeli villa.",
    property_type: "villa",
    property_category: "residential",
    status: "active",
    pricing: { sale_price: "27500000.00", rental_price: null, currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "Ankara",
      district: "Çankaya",
      neighborhood: "Oran",
      street: null,
      latitude: "39.890100",
      longitude: "32.854200",
    },
    building: { net_area_sqm: "320.00", room_count: "5.5", bedroom_count: 5, bathroom_count: 4 },
    features: { has_pool: true, has_garden: true, has_parking: true },
    amenities: ["pool", "parking", "security"],
    image: IMG.villa,
  }),
  prop({
    id: "11111111-1111-1111-1111-111111111104",
    property_code: "FW-TR-BORNOV-00000001",
    slug: "bornova-ofis-kati",
    title: "Bornova Ofis Katı",
    description: "İzmir Bornova A sınıfı ofis.",
    property_type: "office",
    property_category: "commercial",
    status: "active",
    pricing: { sale_price: "14800000.00", rental_price: "180000.00", currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "İzmir",
      district: "Bornova",
      neighborhood: "Erzene",
      street: null,
      latitude: "38.462800",
      longitude: "27.220500",
    },
    building: { net_area_sqm: "240.00", floor_number: 7 },
    features: { has_elevator: true, has_parking: true },
    image: IMG.office,
  }),
  prop({
    id: "11111111-1111-1111-1111-111111111105",
    property_code: "FW-TR-BODRUM-00000001",
    slug: "bodrum-yalikavak-arsa",
    title: "Bodrum Yalıkavak Arsa",
    description: "Yalıkavak imarlı arsa.",
    property_type: "land",
    property_category: "land",
    status: "draft",
    pricing: { sale_price: "42000000.00", rental_price: null, currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "Muğla",
      district: "Bodrum",
      neighborhood: "Yalıkavak",
      street: null,
      latitude: "37.105600",
      longitude: "27.288900",
    },
    building: null,
    features: null,
    image: IMG.land,
  }),
  prop({
    id: "11111111-1111-1111-1111-111111111106",
    property_code: "FW-TR-ATASEH-00000001",
    slug: "atasehir-residence-studyo",
    title: "Ataşehir Residence Stüdyo",
    description: "Merkezi stüdyo daire.",
    property_type: "apartment",
    property_category: "residential",
    status: "active",
    pricing: { sale_price: "4500000.00", rental_price: "32000.00", currency: "TRY", price_on_request: false },
    location: {
      country_code: "TR",
      province: "İstanbul",
      district: "Ataşehir",
      neighborhood: "Barbaros",
      street: null,
      latitude: "40.992300",
      longitude: "29.127800",
    },
    building: { net_area_sqm: "48.00", room_count: "1.0", bedroom_count: 1, bathroom_count: 1 },
    features: { has_elevator: true, has_security: true },
    image: IMG.apartment,
  }),
];

function toSummary(p: DemoProperty) {
  return {
    id: p.id,
    property_code: p.property_code,
    slug: p.slug,
    title: p.title,
    property_type: p.property_type,
    status: p.status,
    sale_price: p.pricing.sale_price,
    rental_price: p.pricing.rental_price,
    currency: p.pricing.currency,
    province: p.location.province,
    district: p.location.district,
    neighborhood: p.location.neighborhood,
    latitude: p.location.latitude,
    longitude: p.location.longitude,
    net_area_sqm: (p.building?.net_area_sqm as string | undefined) ?? null,
    room_count: (p.building?.room_count as string | undefined) ?? null,
    bathroom_count: (p.building?.bathroom_count as number | undefined) ?? null,
    primary_image_url: p.images.find((i) => i.is_primary)?.url ?? p.images[0]?.url ?? null,
    distance_meters: null,
    created_at: p.created_at,
  };
}

function statistics() {
  const by_status: Record<string, number> = {};
  const by_type: Record<string, number> = {};
  const by_province: Record<string, number> = {};
  for (const p of DEMO_PROPERTIES) {
    by_status[p.status] = (by_status[p.status] || 0) + 1;
    by_type[p.property_type] = (by_type[p.property_type] || 0) + 1;
    by_province[p.location.province] = (by_province[p.location.province] || 0) + 1;
  }
  const prices = DEMO_PROPERTIES.map((p) => Number(p.pricing.sale_price || 0)).filter((n) => n > 0);
  const total = DEMO_PROPERTIES.length;
  return {
    total_count: total,
    by_status,
    by_type,
    by_province,
    price_stats: {
      avg_sale_price: prices.length ? prices.reduce((a, b) => a + b, 0) / prices.length : null,
      min_sale_price: prices.length ? Math.min(...prices) : null,
      max_sale_price: prices.length ? Math.max(...prices) : null,
    },
    grouped: {},
    total_properties: total,
    active_properties: (by_status.active || 0) + (by_status.listed || 0),
    draft_properties: by_status.draft || 0,
    sold_properties: by_status.sold || 0,
    rented_properties: by_status.rented || 0,
  };
}

function paginate(items: ReturnType<typeof toSummary>[], page: number, pageSize: number) {
  const total = items.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const start = (page - 1) * pageSize;
  return {
    data: items.slice(start, start + pageSize),
    pagination: {
      page,
      page_size: pageSize,
      total_items: total,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_previous: page > 1,
    },
  };
}

export function demoCatalogResponse(
  method: string,
  segments: string[],
  searchParams: URLSearchParams,
  body: unknown
): { status: number; body: unknown } | null {
  const m = method.toUpperCase();
  const path = segments.join("/");

  if (path === "properties/statistics" && m === "GET") {
    return { status: 200, body: { data: statistics(), meta: { source: "demo-catalog" } } };
  }

  if (path === "properties/statistics/price-distribution" && m === "GET") {
    return {
      status: 200,
      body: {
        data: { "0-5M": 1, "5-10M": 1, "10-20M": 2, "20M+": 2 },
        meta: { source: "demo-catalog" },
      },
    };
  }

  if (path === "properties/search" && (m === "GET" || m === "POST")) {
    let page = Number(searchParams.get("page") || 1);
    let pageSize = Number(searchParams.get("page_size") || 20);
    let query = (searchParams.get("query") || "").toLowerCase();
    let status = searchParams.get("status");
    let type = searchParams.get("type");

    if (m === "POST" && body && typeof body === "object") {
      const b = body as Record<string, unknown>;
      const pagination = (b.pagination || {}) as Record<string, unknown>;
      page = Number(pagination.page || page);
      pageSize = Number(pagination.page_size || pageSize);
      query = String(b.query || query).toLowerCase();
      const filters = (b.filters || {}) as Record<string, unknown>;
      if (Array.isArray(filters.status) && filters.status[0]) status = String(filters.status[0]);
      if (Array.isArray(filters.property_types) && filters.property_types[0]) {
        type = String(filters.property_types[0]);
      }
    }

    let items = DEMO_PROPERTIES.map(toSummary);
    if (query) {
      items = items.filter(
        (i) =>
          i.title.toLowerCase().includes(query) ||
          (i.province || "").toLowerCase().includes(query) ||
          (i.district || "").toLowerCase().includes(query)
      );
    }
    if (status) items = items.filter((i) => i.status === status);
    if (type) items = items.filter((i) => i.property_type === type);

    return { status: 200, body: { ...paginate(items, page, pageSize), meta: { source: "demo-catalog" } } };
  }

  if (segments[0] === "properties" && segments.length === 2 && m === "GET") {
    const id = segments[1];
    if (["search", "statistics", "nearby", "map", "bulk", "register"].includes(id)) return null;
    const found = DEMO_PROPERTIES.find((p) => p.id === id || p.slug === id || p.property_code === id);
    if (!found) {
      return {
        status: 404,
        body: { error: { code: "NOT_FOUND", message: "Property not found in demo catalog" } },
      };
    }
    return { status: 200, body: { data: found, meta: { source: "demo-catalog" } } };
  }

  if (path === "lookups/property-types" && m === "GET") {
    return {
      status: 200,
      body: {
        data: [
          { code: "apartment", category: "residential", display_name: { en: "Apartment", tr: "Daire" } },
          { code: "villa", category: "residential", display_name: { en: "Villa", tr: "Villa" } },
          { code: "residence", category: "residential", display_name: { en: "Residence", tr: "Residence" } },
          { code: "office", category: "commercial", display_name: { en: "Office", tr: "Ofis" } },
          { code: "land", category: "land", display_name: { en: "Land", tr: "Arsa" } },
          { code: "store", category: "commercial", display_name: { en: "Store", tr: "Dükkan" } },
        ],
      },
    };
  }

  if (path.startsWith("lookups/") && m === "GET") {
    return { status: 200, body: { data: [] } };
  }

  return null;
}
