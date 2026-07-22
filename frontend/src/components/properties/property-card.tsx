"use client";

import Link from "next/link";
import Image from "next/image";
import { MapPin, Maximize, Bed, Bath, ArrowUpRight } from "lucide-react";
import { PropertyStatusBadge } from "./property-status-badge";
import { PropertySummary } from "@/lib/types/api";
import { formatPrice } from "@/lib/api/client";
import { MotionDiv } from "@/lib/motion";
import { BrandLogo, BrandMark } from "@/components/ui-custom/brand-logo";

interface PropertyCardProps {
  property: PropertySummary;
  index?: number;
}

export function PropertyCard({ property, index = 0 }: PropertyCardProps) {
  const price = property.sale_price || property.rental_price;
  const priceLabel = property.sale_price ? "Sale" : property.rental_price ? "Rent" : null;

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 18, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, delay: Math.min(index, 8) * 0.05, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -4 }}
      className="group overflow-hidden rounded-3xl border border-border/80 bg-white shadow-soft transition-shadow hover:shadow-lift"
    >
      <div className="relative aspect-[16/10] overflow-hidden bg-secondary">
        {property.primary_image_url ? (
          <Image
            src={property.primary_image_url}
            alt={property.title}
            fill
            className="object-cover transition duration-500 group-hover:scale-[1.04]"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="relative flex h-full items-center justify-center bg-gradient-to-br from-[#EEF3F5] to-[#E8F0F8] text-[#0B4C84]/40">
            <BrandMark className="absolute inset-0 m-auto h-16 w-auto opacity-[0.12]" />
            <MapPin className="relative h-12 w-12" strokeWidth={1.25} />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-[#16212B]/45 via-transparent to-transparent opacity-80" />
        <div className="absolute left-3 top-3 flex items-center gap-2">
          <PropertyStatusBadge status={property.status} />
        </div>
        <div className="absolute right-3 top-3 rounded-lg bg-white/95 px-2 py-1 shadow-soft backdrop-blur">
          <BrandLogo size="xs" href={null} className="h-3.5 w-auto" />
        </div>
        <div className="absolute bottom-3 left-3 right-3 flex items-end justify-between gap-2">
          <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-white/85">
            {property.property_type}
          </p>
          <p className="rounded-xl bg-white/95 px-2.5 py-1 text-[13px] font-semibold text-foreground shadow-soft backdrop-blur">
            {formatPrice(price, property.currency)}
            {priceLabel && (
              <span className="ml-1 text-[10px] font-medium text-muted-foreground">{priceLabel}</span>
            )}
          </p>
        </div>
      </div>

      <div className="space-y-3 p-5">
        <div>
          <h3 className="line-clamp-1 font-[family-name:var(--font-display)] text-lg font-semibold tracking-tight">
            {property.title}
          </h3>
          <p className="mt-1 flex items-center gap-1.5 text-[12px] text-muted-foreground">
            <MapPin className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">
              {[property.province, property.district, property.neighborhood]
                .filter(Boolean)
                .join(" · ") || "Location TBD"}
            </span>
          </p>
        </div>

        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[12px] text-muted-foreground">
          {property.net_area_sqm && (
            <span className="inline-flex items-center gap-1">
              <Maximize className="h-3.5 w-3.5" />
              {property.net_area_sqm} m²
            </span>
          )}
          {property.room_count && (
            <span className="inline-flex items-center gap-1">
              <Bed className="h-3.5 w-3.5" />
              {property.room_count}
            </span>
          )}
          {property.bathroom_count != null && (
            <span className="inline-flex items-center gap-1">
              <Bath className="h-3.5 w-3.5" />
              {property.bathroom_count}
            </span>
          )}
        </div>

        <Link
          href={`/properties/${property.id}`}
          className="inline-flex h-10 w-full items-center justify-center gap-2 rounded-2xl border border-border bg-secondary/60 text-[13px] font-semibold text-foreground transition hover:border-primary/30 hover:bg-accent hover:text-primary"
        >
          Open dossier
          <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>
    </MotionDiv>
  );
}
