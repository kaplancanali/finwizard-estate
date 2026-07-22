import type { Metadata } from "next";
import { Suspense } from "react";
import { Manrope, Fraunces } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Shell } from "@/components/ui-custom/shell";
import { AuthProvider, RequireAuth } from "@/components/auth/auth-provider";
import "./globals.css";

const manrope = Manrope({
  variable: "--font-sans",
  subsets: ["latin"],
  display: "swap",
});

const fraunces = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  applicationName: "Torkam",
  title: {
    default: "Torkam",
    template: "%s · Torkam",
  },
  description: "Torkam Holding property intelligence platform.",
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/torkam-logo.svg", type: "image/svg+xml", sizes: "any" },
    ],
    apple: [{ url: "/apple-icon.svg", type: "image/svg+xml" }],
    shortcut: ["/icon.svg"],
  },
  openGraph: {
    title: "Torkam",
    description: "Torkam Holding property intelligence platform.",
    siteName: "Torkam",
    images: [{ url: "/torkam-logo.svg" }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="tr"
      className={`${manrope.variable} ${fraunces.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <TooltipProvider>
          <AuthProvider>
            <RequireAuth>
              <Shell>
                <Suspense fallback={null}>{children}</Suspense>
              </Shell>
            </RequireAuth>
          </AuthProvider>
          <Toaster position="top-right" richColors closeButton />
        </TooltipProvider>
      </body>
    </html>
  );
}
