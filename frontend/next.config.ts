import type { NextConfig } from "next";

/**
 * API traffic is handled by `src/app/api/v1/[...path]/route.ts`:
 * - proxies to BACKEND_URL when it is a public URL
 * - otherwise serves the local demo catalog (needed on Vercel without a public API)
 */
const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "images.unsplash.com" },
      { protocol: "https", hostname: "**" },
    ],
  },
};

export default nextConfig;
