import { toast } from "sonner";

/**
 * Browser calls same-origin `/api/v1` (proxied by Next.js rewrites to BACKEND_URL).
 * Override with NEXT_PUBLIC_API_BASE_URL only if you need a direct backend URL.
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "/api/v1";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: Array<{ field?: string; message: string; code?: string }>,
    public readonly correlationId?: string | null
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
}

function resolveRequestUrl(path: string, params?: FetchOptions["params"]): string {
  const base = API_BASE_URL.replace(/\/$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  let full =
    path.startsWith("http://") || path.startsWith("https://")
      ? path
      : `${base}${normalizedPath}`;

  if (params) {
    const search = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        search.set(key, String(value));
      }
    });
    const qs = search.toString();
    if (qs) {
      full += (full.includes("?") ? "&" : "?") + qs;
    }
  }
  return full;
}

async function parseError(response: Response): Promise<ApiError> {
  let code = "unknown";
  let message = `Request failed with status ${response.status}`;
  let details: Array<{ field?: string; message: string; code?: string }> | undefined;
  let correlationId: string | null | undefined;
  try {
    const payload = await response.json();
    if (payload.error) {
      code = payload.error.code || code;
      message = payload.error.message || message;
      details = payload.error.details;
      correlationId = payload.error.correlation_id;
    } else if (payload.message) {
      message = payload.message;
    }
  } catch {
    // ignore parsing failure
  }
  return new ApiError(response.status, code, message, details, correlationId);
}

async function request<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const url = resolveRequestUrl(path, options.params);
  const headers = new Headers(options.headers);
  if (options.body && typeof options.body === "string" && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  if (typeof window !== "undefined" && !headers.has("Authorization")) {
    try {
      const raw = localStorage.getItem("torkam.auth.session");
      if (raw) {
        const session = JSON.parse(raw) as { token?: string; expiresAt?: number };
        if (session.token && (!session.expiresAt || Date.now() < session.expiresAt)) {
          headers.set("Authorization", `Bearer ${session.token}`);
        }
      }
    } catch {
      // ignore malformed session
    }
  }

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (err) {
    const message =
      err instanceof TypeError
        ? "API sunucusuna bağlanılamadı. Backend çalışıyor mu? (Docker: make docker-up)"
        : err instanceof Error
          ? err.message
          : "Bağlantı hatası";
    throw new ApiError(0, "network_error", message);
  }

  if (response.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("torkam.auth.session");
    if (!window.location.pathname.startsWith("/login")) {
      window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
    }
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function get<T>(path: string, params?: FetchOptions["params"], options?: RequestInit) {
  return request<T>(path, { method: "GET", params, ...options });
}

export function post<T>(path: string, body: unknown, options?: RequestInit) {
  return request<T>(path, { method: "POST", body: JSON.stringify(body), ...options });
}

export function put<T>(path: string, body: unknown, options?: RequestInit) {
  return request<T>(path, { method: "PUT", body: JSON.stringify(body), ...options });
}

export function patch<T>(path: string, body: unknown, options?: RequestInit) {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body), ...options });
}

export function del<T>(path: string, options?: RequestInit) {
  return request<T>(path, { method: "DELETE", ...options });
}

export function handleApiError(error: unknown): string {
  if (error instanceof ApiError) {
    const detail = error.details?.map((d) => d.message).join(", ") || error.message;
    if (error.code === "network_error") {
      toast.error("Bağlantı hatası", { description: detail });
    } else {
      toast.error(`Hata (${error.status})`, { description: detail });
    }
    return detail;
  }
  if (error instanceof Error) {
    toast.error("Beklenmedik hata", { description: error.message });
    return error.message;
  }
  toast.error("Beklenmedik hata");
  return "Bilinmeyen hata";
}

export function formatPrice(amount?: string | number | null, currency?: string | null): string {
  if (amount === undefined || amount === null || amount === "") return "—";
  const value = typeof amount === "string" ? parseFloat(amount) : amount;
  if (Number.isNaN(value)) return "—";
  return new Intl.NumberFormat("tr-TR", {
    style: "currency",
    currency: currency || "TRY",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString("tr-TR");
}

export function statusVariant(status: string): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "active":
      return "default";
    case "draft":
      return "secondary";
    case "pending_review":
      return "outline";
    case "sold":
    case "rented":
      return "default";
    case "paused":
    case "archived":
    case "deleted":
      return "destructive";
    default:
      return "secondary";
  }
}

export { API_BASE_URL };
