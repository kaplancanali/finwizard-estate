export type PropertyStatus =
  | "draft"
  | "pending_review"
  | "active"
  | "paused"
  | "sold"
  | "rented"
  | "archived"
  | "deleted";

export type PropertyType =
  | "apartment"
  | "house"
  | "villa"
  | "office"
  | "shop"
  | "land"
  | "warehouse"
  | "building";

export type PropertyCategory = "residential" | "commercial" | "land";
export type PropertyVisibility = "private" | "public" | "restricted";
export type SourceType = "manual" | "import" | "listing_url" | "api" | "bulk_import";

export interface Pricing {
  sale_price?: string | null;
  rental_price?: string | null;
  maintenance_fee?: string | null;
  currency: string;
  price_on_request?: boolean;
}

export interface Location {
  country_code: string;
  province?: string | null;
  district?: string | null;
  neighborhood?: string | null;
  street?: string | null;
  postal_code?: string | null;
  address_line?: string | null;
  latitude?: string | null;
  longitude?: string | null;
  elevation?: string | null;
}

export interface Parcel {
  block?: string | null;
  parcel_number?: string | null;
  parcel_area_sqm?: string | null;
  cadastral_reference?: string | null;
  zoning_type?: string | null;
}

export interface Building {
  construction_year?: number | null;
  floor_count?: number | null;
  floor_number?: number | null;
  unit_number?: string | null;
  net_area_sqm?: string | null;
  gross_area_sqm?: string | null;
  room_count?: string | null;
  living_room_count?: number | null;
  bedroom_count?: number | null;
  bathroom_count?: number | null;
  balcony_count?: number | null;
  parking_count?: number | null;
}

export interface Features {
  heating_type?: string | null;
  cooling_type?: string | null;
  energy_certificate_class?: string | null;
  has_elevator?: boolean;
  has_parking?: boolean;
  has_balcony?: boolean;
  has_garden?: boolean;
  has_pool?: boolean;
  has_security?: boolean;
  has_storage?: boolean;
  has_smart_home?: boolean;
  has_solar?: boolean;
  has_ev_charger?: boolean;
  accessibility_level?: string | null;
}

export interface Source {
  source_type?: SourceType;
  source_reference?: string | null;
  source_payload?: Record<string, unknown> | null;
}

export interface Image {
  id: string;
  url?: string | null;
  is_primary?: boolean;
  sort_order?: number;
  caption?: string | null;
}

export interface Document {
  id: string;
  document_type: string;
  url?: string | null;
  verified?: boolean;
}

export interface Ownership {
  id: string;
  owner_name: string;
  ownership_percentage: string;
  is_current?: boolean;
}

export interface Property {
  id: string;
  tenant_id: string;
  property_code: string;
  slug: string;
  title: string;
  description?: string | null;
  property_type: PropertyType;
  property_category: PropertyCategory;
  property_subtype?: string | null;
  status: PropertyStatus;
  visibility: PropertyVisibility;
  pricing?: Pricing | null;
  location: Location;
  parcel?: Parcel | null;
  building?: Building | null;
  features?: Features | null;
  amenities: string[];
  tags: string[];
  images?: Image[] | null;
  documents?: Document[] | null;
  listing?: Record<string, unknown> | null;
  ownership?: Ownership[] | null;
  metadata?: Record<string, unknown> | null;
  version: number;
  published_at?: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by?: string | null;
}

export interface PropertySummary {
  id: string;
  property_code: string;
  slug: string;
  title: string;
  property_type: PropertyType;
  status: PropertyStatus;
  sale_price?: string | null;
  rental_price?: string | null;
  currency?: string | null;
  province?: string | null;
  district?: string | null;
  neighborhood?: string | null;
  latitude?: string | null;
  longitude?: string | null;
  net_area_sqm?: string | null;
  room_count?: string | null;
  bathroom_count?: number | null;
  primary_image_url?: string | null;
  distance_meters?: number | null;
  created_at?: string | null;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export interface ResponseMeta {
  correlation_id?: string | null;
  request_id?: string | null;
}

export interface ApiResponse<T> {
  data: T;
  meta: ResponseMeta;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: PaginationMeta;
  meta: ResponseMeta;
}

export interface RangeFilter {
  min?: number | null;
  max?: number | null;
}

export interface GeoRadiusFilter {
  type: "radius";
  latitude: number | string;
  longitude: number | string;
  radius_meters: number;
}

export interface SortField {
  field: string;
  direction: "asc" | "desc";
}

export interface SearchFilters {
  property_types?: PropertyType[];
  property_categories?: PropertyCategory[];
  status?: PropertyStatus[];
  sale_price?: RangeFilter;
  rental_price?: RangeFilter;
  net_area_sqm?: RangeFilter;
  room_count?: RangeFilter;
  bathroom_count?: RangeFilter;
  construction_year?: RangeFilter;
  country_code?: string;
  provinces?: string[];
  districts?: string[];
  heating_types?: string[];
  amenities?: string[];
  features?: Record<string, boolean>;
  tags?: string[];
}

export interface PropertySearchRequest {
  query?: string;
  filters?: SearchFilters;
  geo?: GeoRadiusFilter;
  sort?: SortField[];
  pagination?: { page: number; page_size: number };
  include_facets?: boolean;
}

export interface LookupItem {
  code: string;
  name?: string;
}

export interface StatusHistoryItem {
  id: string;
  old_status?: string;
  new_status?: string;
  changed_by?: string;
  reason?: string | null;
}

export interface PriceHistoryItem {
  id: string;
  price_type: string;
  old_amount?: string | null;
  new_amount?: string | null;
  currency?: string;
  changed_by?: string;
  change_reason?: string | null;
}

export interface TenantStatistics {
  total_count?: number;
  total_properties?: number;
  active_properties?: number;
  draft_properties?: number;
  sold_properties?: number;
  rented_properties?: number;
  by_type?: Record<string, number>;
  by_status?: Record<string, number>;
  by_province?: Record<string, number>;
  price_stats?: Record<string, number | null>;
}

export type PropertyCreateRequest = Omit<
  Property,
  | "id"
  | "tenant_id"
  | "property_code"
  | "slug"
  | "version"
  | "created_at"
  | "updated_at"
  | "created_by"
  | "updated_by"
  | "published_at"
  | "images"
  | "documents"
  | "listing"
  | "ownership"
  | "metadata"
>;

export interface PropertyUpdateRequest {
  version: number;
  title?: string;
  description?: string | null;
  pricing?: Pricing | null;
  location?: Location | null;
  parcel?: Parcel | null;
  building?: Building | null;
  features?: Features | null;
  amenities?: string[];
  tags?: string[];
}

export interface StatusChangeRequest {
  version: number;
  status: PropertyStatus;
  reason?: string;
}

export interface RegisterPropertyRequest {
  title?: string;
  property_type?: PropertyType;
  property_category?: PropertyCategory;
  source_type: SourceType;
  source_reference?: string;
  location?: Location;
  options?: Record<string, unknown>;
}

export interface ImageUploadRequest {
  file_name: string;
  mime_type: string;
  file_size: number;
  caption?: string;
  is_primary?: boolean;
  sort_order?: number;
}

export interface ImageUploadResult {
  image: { id: string; storage_key: string; url?: string };
  upload_url: string;
  property_version: number;
}
