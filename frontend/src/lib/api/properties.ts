import {
  ApiResponse,
  PaginatedResponse,
  Property,
  PropertyCreateRequest,
  PropertySearchRequest,
  PropertySummary,
  PropertyUpdateRequest,
  RegisterPropertyRequest,
  StatusChangeRequest,
  TenantStatistics,
  ImageUploadRequest,
  ImageUploadResult,
  LookupItem,
  PriceHistoryItem,
  StatusHistoryItem,
} from "@/lib/types/api";
import { del, get, patch, post, put } from "./client";

export function searchProperties(body: PropertySearchRequest) {
  return post<PaginatedResponse<PropertySummary>>("/properties/search", body);
}

export function getProperties(params?: {
  page?: number;
  page_size?: number;
  type?: string;
  status?: string;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  rooms?: number;
  province?: string;
  district?: string;
  lat?: number;
  lng?: number;
  radius?: number;
}) {
  return get<PaginatedResponse<PropertySummary>>("/properties/search", params);
}

export function getProperty(id: string, include?: string) {
  return get<ApiResponse<Property>>(`/properties/${id}`, include ? { include } : undefined);
}

export function getPropertyByCode(code: string, include?: string) {
  return get<ApiResponse<Property>>(`/properties/code/${code}`, include ? { include } : undefined);
}

export function getPropertyBySlug(slug: string, include?: string) {
  return get<ApiResponse<Property>>(`/properties/slug/${slug}`, include ? { include } : undefined);
}

export function createProperty(body: PropertyCreateRequest) {
  return post<ApiResponse<Property>>("/properties", body);
}

export function registerProperty(body: RegisterPropertyRequest) {
  return post<ApiResponse<Property>>("/properties/register", body);
}

export function updateProperty(id: string, body: PropertyUpdateRequest) {
  return patch<ApiResponse<Property>>(`/properties/${id}`, body);
}

export function replaceProperty(id: string, body: PropertyUpdateRequest) {
  return put<ApiResponse<Property>>(`/properties/${id}`, body);
}

export function deleteProperty(id: string) {
  return del<void>(`/properties/${id}`);
}

export function restoreProperty(id: string) {
  return post<ApiResponse<Property>>(`/properties/${id}/restore`, {});
}

export function changeStatus(id: string, body: StatusChangeRequest) {
  return post<ApiResponse<Property>>(`/properties/${id}/status`, body);
}

export function getNearby(lat: number, lng: number, radius = 5000, limit = 20) {
  return get<PaginatedResponse<PropertySummary>>("/properties/nearby", {
    lat,
    lng,
    radius,
    limit,
  });
}

export function getStatistics(group_by?: string) {
  return get<ApiResponse<TenantStatistics>>("/properties/statistics", group_by ? { group_by } : undefined);
}

export function getPriceDistribution() {
  return get<ApiResponse<Record<string, number>>>("/properties/statistics/price-distribution");
}

export function getPriceHistory(id: string, page = 1, page_size = 20) {
  return get<PaginatedResponse<PriceHistoryItem>>(`/properties/${id}/history/price`, { page, page_size });
}

export function getStatusHistory(id: string, page = 1, page_size = 20) {
  return get<PaginatedResponse<StatusHistoryItem>>(`/properties/${id}/history/status`, { page, page_size });
}

export function initiateImageUpload(id: string, body: ImageUploadRequest) {
  return post<ApiResponse<ImageUploadResult>>(`/properties/${id}/images`, body);
}

export function confirmImageUpload(id: string, imageId: string) {
  return post<ApiResponse<Property>>(`/properties/${id}/images/${imageId}/confirm`, {});
}

export function deleteImage(id: string, imageId: string) {
  return del<void>(`/properties/${id}/images/${imageId}`);
}

export function getPropertyTypes() {
  return get<ApiResponse<LookupItem[]>>("/lookups/property-types");
}

export function getStatuses() {
  return get<ApiResponse<LookupItem[]>>("/lookups/statuses");
}

export function getAmenities() {
  return get<ApiResponse<LookupItem[]>>("/lookups/amenities");
}

export { get as getLookups };
