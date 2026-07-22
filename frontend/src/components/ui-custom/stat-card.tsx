"use client";

import { cn } from "@/lib/utils";
import { MotionDiv } from "@/lib/motion";

interface StatCardProps {
  title: string;
  value: React.ReactNode;
  icon?: React.ReactNode;
  loading?: boolean;
  description?: string;
  trend?: { value: string; positive?: boolean };
  accent?: "green" | "navy" | "neutral";
  index?: number;
}

export function StatCard({
  title,
  value,
  icon,
  loading,
  description,
  trend,
  accent = "green",
  index = 0,
}: StatCardProps) {
  const accentBar =
    accent === "navy"
      ? "from-[#0B4C84] to-[#124775]"
      : accent === "neutral"
        ? "from-[#66788A] to-[#DCE5EA]"
        : "from-[#0C8A43] to-[#2E9E67]";

  return (
    <MotionDiv
      initial={{ opacity: 0, y: 18, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.4, delay: index * 0.06, ease: [0.22, 1, 0.36, 1] }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className={cn(
        "group relative overflow-hidden rounded-2xl border border-border/80 bg-white p-5 shadow-soft",
        "transition-shadow hover:shadow-lift"
      )}
    >
      <div className={cn("absolute inset-x-0 top-0 h-1 bg-gradient-to-r opacity-90", accentBar)} />
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[12px] font-medium uppercase tracking-[0.08em] text-muted-foreground">
            {title}
          </p>
          {loading ? (
            <div className="mt-3 h-9 w-24 animate-pulse rounded-lg bg-secondary" />
          ) : (
            <p className="mt-2 font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight tabular-nums">
              {value}
            </p>
          )}
        </div>
        {icon && (
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary text-primary transition group-hover:bg-accent">
            {icon}
          </div>
        )}
      </div>
      <div className="mt-4 flex items-center justify-between gap-2">
        {description && <p className="text-[12px] text-muted-foreground">{description}</p>}
        {trend && (
          <span
            className={cn(
              "rounded-full px-2 py-0.5 text-[11px] font-semibold",
              trend.positive ? "bg-accent text-primary" : "bg-secondary text-muted-foreground"
            )}
          >
            {trend.value}
          </span>
        )}
      </div>
    </MotionDiv>
  );
}
