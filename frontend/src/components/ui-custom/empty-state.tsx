"use client";

import Link from "next/link";
import { cn } from "@/lib/utils";
import { MotionDiv } from "@/lib/motion";
import { Button } from "@/components/ui/button";
import { BrandLogo, BrandMark } from "@/components/ui-custom/brand-logo";
import { brand } from "@/lib/design-system";

interface EmptyStateProps {
  title?: string;
  description?: string;
  action?: React.ReactNode;
  secondaryAction?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  title = "Nothing here yet",
  description,
  action,
  secondaryAction,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <MotionDiv
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "relative flex flex-col items-center justify-center overflow-hidden rounded-3xl border border-dashed border-border bg-white/70 px-8 py-16 text-center shadow-soft",
        className
      )}
    >
      <BrandMark className="absolute right-6 top-6 h-10 w-auto" />
      <div className="mb-5 flex flex-col items-center gap-3">
        <div className="rounded-2xl border border-border bg-white px-4 py-2.5 shadow-soft">
          <BrandLogo size="sm" href={null} />
        </div>
        {icon ? (
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-secondary text-primary">
            {icon}
          </div>
        ) : null}
      </div>
      <h3 className="font-[family-name:var(--font-display)] text-lg font-semibold tracking-tight">{title}</h3>
      {description && (
        <p className="mt-2 max-w-sm text-[14px] leading-relaxed text-muted-foreground">{description}</p>
      )}
      <p className="mt-3 text-[11px] font-medium uppercase tracking-[0.16em] text-primary/70">
        {brand.name}
      </p>
      {(action || secondaryAction) && (
        <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
          {action}
          {secondaryAction}
        </div>
      )}
    </MotionDiv>
  );
}

export function EmptyStateCTA({
  href,
  label,
  variant = "default",
}: {
  href: string;
  label: string;
  variant?: "default" | "outline";
}) {
  return (
    <Button asChild variant={variant === "outline" ? "outline" : "default"} className="rounded-xl">
      <Link href={href}>{label}</Link>
    </Button>
  );
}
