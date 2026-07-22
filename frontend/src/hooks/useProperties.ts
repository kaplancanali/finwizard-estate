"use client";

import { useCallback, useEffect, useState } from "react";
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
} from "@/lib/types/api";
import { handleApiError } from "@/lib/api/client";
import * as api from "@/lib/api/properties";

interface UsePropertiesOptions {
  initialPage?: number;
  pageSize?: number;
  autoFetch?: boolean;
}

export function useProperties(options: UsePropertiesOptions = {}) {
  const { initialPage = 1, pageSize = 20, autoFetch = true } = options;
  const [items, setItems] = useState<PropertySummary[]>([]);
  const [pagination, setPagination] = useState<PaginatedResponse<PropertySummary>["pagination"] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(
    async (body: PropertySearchRequest) => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.searchProperties({
          pagination: { page: initialPage, page_size: pageSize },
          ...body,
        });
        setItems(result.data);
        setPagination(result.pagination);
        return result;
      } catch (err) {
        const message = handleApiError(err);
        setError(message);
        return undefined;
      } finally {
        setLoading(false);
      }
    },
    [initialPage, pageSize]
  );

  const fetchList = useCallback(
    async (params?: {
      page?: number;
      page_size?: number;
      type?: string;
      status?: string;
      province?: string;
      district?: string;
    }) => {
      setLoading(true);
      setError(null);
      try {
        const result = await api.getProperties({
          page: initialPage,
          page_size: pageSize,
          ...params,
        });
        setItems(result.data);
        setPagination(result.pagination);
        return result;
      } catch (err) {
        const message = handleApiError(err);
        setError(message);
        return undefined;
      } finally {
        setLoading(false);
      }
    },
    [initialPage, pageSize]
  );

  useEffect(() => {
    if (autoFetch) {
      void fetchList();
    }
  }, [autoFetch, fetchList]);

  return { items, pagination, loading, error, search, fetchList };
}

export function useProperty(id?: string, include?: string) {
  const [property, setProperty] = useState<Property | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.getProperty(id, include);
      setProperty(response.data);
      return response.data;
    } catch (err) {
      const message = handleApiError(err);
      setError(message);
      return undefined;
    } finally {
      setLoading(false);
    }
  }, [id, include]);

  useEffect(() => {
    void fetch();
  }, [fetch]);

  const mutate = useCallback(
    async (mutator: (prev: Property) => Promise<ApiResponse<Property>> | Promise<Property>) => {
      if (!property) return;
      try {
        const result = await mutator(property);
        const next = "data" in result ? result.data : result;
        setProperty(next);
        return next;
      } catch (err) {
        handleApiError(err);
        return undefined;
      }
    },
    [property]
  );

  return { property, loading, error, refresh: fetch, mutate, setProperty };
}

export function useStatistics() {
  const [statistics, setStatistics] = useState<TenantStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.getStatistics();
      setStatistics(response.data);
      return response.data;
    } catch (err) {
      const message = handleApiError(err);
      setError(message);
      return undefined;
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetch();
  }, [fetch]);

  return { statistics, loading, error, refresh: fetch };
}

export function usePropertyMutations() {
  const [loading, setLoading] = useState(false);

  const create = useCallback(async (body: PropertyCreateRequest) => {
    setLoading(true);
    try {
      const response = await api.createProperty(body);
      return response.data;
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (body: RegisterPropertyRequest) => {
    setLoading(true);
    try {
      const response = await api.registerProperty(body);
      return response.data;
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const update = useCallback(async (id: string, body: PropertyUpdateRequest) => {
    setLoading(true);
    try {
      const response = await api.updateProperty(id, body);
      return response.data;
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const changeStatus = useCallback(async (id: string, body: StatusChangeRequest) => {
    setLoading(true);
    try {
      const response = await api.changeStatus(id, body);
      return response.data;
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(async (id: string) => {
    setLoading(true);
    try {
      await api.deleteProperty(id);
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const restore = useCallback(async (id: string) => {
    setLoading(true);
    try {
      const response = await api.restoreProperty(id);
      return response.data;
    } catch (err) {
      handleApiError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { create, register, update, changeStatus, remove, restore, loading };
}

export function useLookups() {
  const [propertyTypes, setPropertyTypes] = useState<{ code: string }[]>([]);
  const [statuses, setStatuses] = useState<{ code: string }[]>([]);
  const [amenities, setAmenities] = useState<{ code: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const [types, st, am] = await Promise.all([
        api.getPropertyTypes(),
        api.getStatuses(),
        api.getAmenities(),
      ]);
      setPropertyTypes(types.data);
      setStatuses(st.data);
      setAmenities(am.data);
    } catch (err) {
      handleApiError(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetch();
  }, [fetch]);

  return { propertyTypes, statuses, amenities, loading, refresh: fetch };
}
