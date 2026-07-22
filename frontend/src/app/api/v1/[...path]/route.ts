import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { demoCatalogResponse } from "@/lib/demo/catalog";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function backendBase(): string | null {
  const raw = (process.env.BACKEND_URL || "").trim().replace(/\/$/, "");
  if (!raw) return null;
  // Serverless cannot reach the developer's local machine.
  if (/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(raw)) {
    return null;
  }
  return raw;
}

async function proxyToBackend(request: NextRequest, pathSegments: string[]): Promise<Response | null> {
  const base = backendBase();
  if (!base) return null;

  const subpath = pathSegments.join("/");
  const url = new URL(request.url);
  const target = `${base}/api/v1/${subpath}${url.search}`;

  const headers = new Headers();
  const accept = request.headers.get("accept");
  const contentType = request.headers.get("content-type");
  const authorization = request.headers.get("authorization");
  const correlation = request.headers.get("x-correlation-id");
  if (accept) headers.set("accept", accept);
  if (contentType) headers.set("content-type", contentType);
  if (authorization) headers.set("authorization", authorization);
  if (correlation) headers.set("x-correlation-id", correlation);

  const method = request.method.toUpperCase();
  const init: RequestInit = { method, headers, cache: "no-store" };
  if (method !== "GET" && method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  try {
    const upstream = await fetch(target, init);
    const body = await upstream.arrayBuffer();
    const responseHeaders = new Headers();
    const upstreamType = upstream.headers.get("content-type");
    if (upstreamType) responseHeaders.set("content-type", upstreamType);
    return new NextResponse(body, { status: upstream.status, headers: responseHeaders });
  } catch {
    return null;
  }
}

async function handle(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const segments = path || [];

  const proxied = await proxyToBackend(request, segments);
  if (proxied) return proxied;

  const demo = demoCatalogResponse(request.method, segments, request.nextUrl.searchParams, await safeJson(request));
  if (demo) return NextResponse.json(demo.body, { status: demo.status });

  return NextResponse.json(
    {
      error: {
        code: "BACKEND_UNAVAILABLE",
        message:
          "Property API is not configured. Set BACKEND_URL on Vercel to a public property-service URL, or use the local demo catalog.",
      },
    },
    { status: 503 }
  );
}

async function safeJson(request: NextRequest): Promise<unknown> {
  try {
    if (request.method === "GET" || request.method === "HEAD") return null;
    return await request.json();
  } catch {
    return null;
  }
}

export const GET = handle;
export const POST = handle;
export const PUT = handle;
export const PATCH = handle;
export const DELETE = handle;
