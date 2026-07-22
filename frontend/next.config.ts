import type { NextConfig } from "next";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8001";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "**" },
    ],
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${BACKEND_URL}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${BACKEND_URL}/health`,
      },
      {
        source: "/health/:path*",
        destination: `${BACKEND_URL}/health/:path*`,
      },
    ];
  },
};

export default nextConfig;
