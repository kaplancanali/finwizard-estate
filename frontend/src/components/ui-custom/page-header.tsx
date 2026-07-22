"use client";

import { cn } from "@/lib/utils";
import { MotionDiv } from "@/lib/motion";
import { BrandLogo } from "@/components/ui-custom/brand-logo";
import { brand } from "@/lib/design-system";

interface PageHeaderProps {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
  showLogo?: boolean;
}

export function PageHeader({
  eyebrow,
  title,
  description,
  action,
  className,
  showLogo = true,
}: PageHeaderProps) {
  return (
    <MotionDiv
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between",
        className
      )}
    >
      <div className="max-w-2xl space-y-2">
        <div className="flex items-center gap-3">
          {showLogo && (
            <span className="hidden rounded-xl border border-border bg-white px-2.5 py-1.5 shadow-soft sm:inline-flex">
              <BrandLogo size="xs" href={null} />
            </span>
          )}
          {eyebrow && (
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">
              {brand.name} · {eyebrow}
            </p>
          )}
        </div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight text-foreground sm:text-4xl text-balance">
          {title}
        </h1>
        {description && (
          <p className="text-[15px] leading-relaxed text-muted-foreground">{description}</p>
        )}
      </div>
      {action && <div className="flex shrink-0 items-center gap-2">{action}</div>}
    </MotionDiv>
  );
}
