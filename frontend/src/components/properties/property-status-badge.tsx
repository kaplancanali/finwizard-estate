"use client";

import { statusTone } from "@/lib/design-system";
import { cn } from "@/lib/utils";

interface PropertyStatusBadgeProps {
  status: string;
  className?: string;
}

const labels: Record<string, string> = {
  draft: "Draft",
  pending_review: "In review",
  active: "Active",
  paused: "Paused",
  sold: "Sold",
  rented: "Rented",
  archived: "Archived",
  deleted: "Deleted",
};

export function PropertyStatusBadge({ status, className }: PropertyStatusBadgeProps) {
  const tone = statusTone[status] || statusTone.draft;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold tracking-wide",
        className
      )}
      style={{
        background: tone.bg,
        color: tone.fg,
        boxShadow: `inset 0 0 0 1px ${tone.ring}33`,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ background: tone.fg }} />
      {labels[status] || status}
    </span>
  );
}
