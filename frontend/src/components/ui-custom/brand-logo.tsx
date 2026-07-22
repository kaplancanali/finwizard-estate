"use client";

import Image from "next/image";
import Link from "next/link";
import { brand } from "@/lib/design-system";
import { cn } from "@/lib/utils";

type LogoSize = "xs" | "sm" | "md" | "lg" | "xl" | "hero";

const sizeMap: Record<LogoSize, { width: number; height: number; className: string }> = {
  xs: { width: 72, height: 20, className: "h-4 w-auto" },
  sm: { width: 100, height: 28, className: "h-6 w-auto" },
  md: { width: 132, height: 38, className: "h-8 w-auto sm:h-9" },
  lg: { width: 180, height: 52, className: "h-10 w-auto sm:h-12" },
  xl: { width: 240, height: 68, className: "h-14 w-auto sm:h-16" },
  hero: { width: 320, height: 90, className: "h-16 w-auto sm:h-20 lg:h-24" },
};

interface BrandLogoProps {
  size?: LogoSize;
  className?: string;
  href?: string | null;
  priority?: boolean;
  invert?: boolean;
  showWordmark?: boolean;
}

export function BrandLogo({
  size = "md",
  className,
  href = "/",
  priority = false,
  invert = false,
  showWordmark = false,
}: BrandLogoProps) {
  const dims = sizeMap[size];
  const image = (
    <Image
      src={brand.logo}
      alt={brand.name}
      width={dims.width}
      height={dims.height}
      priority={priority}
      className={cn(dims.className, invert && "brightness-0 invert", className)}
    />
  );

  const content = showWordmark ? (
    <span className="inline-flex items-center gap-2.5">
      {image}
      <span className="font-[family-name:var(--font-display)] text-sm font-semibold tracking-tight text-foreground">
        {brand.name}
      </span>
    </span>
  ) : (
    image
  );

  if (href === null) return content;
  return (
    <Link href={href} className="inline-flex items-center transition hover:opacity-90" aria-label={brand.name}>
      {content}
    </Link>
  );
}

/** Soft watermark logo for cards / empty surfaces */
export function BrandMark({ className }: { className?: string }) {
  return (
    <Image
      src={brand.logo}
      alt=""
      width={200}
      height={56}
      aria-hidden
      className={cn("pointer-events-none select-none opacity-[0.07]", className)}
    />
  );
}
