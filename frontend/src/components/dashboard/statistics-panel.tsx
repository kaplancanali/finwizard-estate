"use client";

import Link from "next/link";
import {
  ArrowUpRight,
  Building2,
  CheckCircle2,
  Clock,
  Sparkles,
  TrendingUp,
  FileCheck2,
  Plus,
  Search,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useStatistics } from "@/hooks/useProperties";
import { brand } from "@/lib/design-system";
import { BrandLogo, BrandMark } from "@/components/ui-custom/brand-logo";
import { StatCard } from "@/components/ui-custom/stat-card";
import { DashboardSkeleton } from "@/components/ui-custom/skeleton";
import { EmptyState, EmptyStateCTA } from "@/components/ui-custom/empty-state";
import { MotionDiv, staggerContainer, listItem } from "@/lib/motion";

const CHART = ["#0C8A43", "#0B4C84", "#2E9E67", "#66788A", "#124775"];

const quickActions = [
  {
    href: "/properties/new",
    title: "Register asset",
    desc: "Create a new property record",
    icon: Plus,
  },
  {
    href: "/properties/search",
    title: "Discover",
    desc: "Advanced portfolio search",
    icon: Search,
  },
  {
    href: "/properties",
    title: "Browse portfolio",
    desc: "All holdings at a glance",
    icon: Building2,
  },
];

export function StatisticsPanel() {
  const { statistics, loading, error } = useStatistics();

  if (loading) return <DashboardSkeleton />;
  if (error) {
    return (
      <EmptyState
        title="Unable to load overview"
        description={error}
        action={<EmptyStateCTA href="/properties" label="Go to portfolio" />}
        secondaryAction={<EmptyStateCTA href="/" label="Retry" variant="outline" />}
      />
    );
  }

  const typeData = Object.entries(statistics?.by_type || {}).map(([name, value]) => ({
    name,
    value,
  }));
  const statusData = Object.entries(statistics?.by_status || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="space-y-8">
      {/* Hero — Torkam banner */}
      <MotionDiv
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="relative overflow-hidden rounded-[28px] gradient-hero p-8 text-white shadow-lift sm:p-10"
      >
        <div className="pointer-events-none absolute -right-16 -top-20 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 left-1/3 h-64 w-64 rounded-full bg-[#2E9E67]/30 blur-3xl" />
        <BrandMark className="absolute -right-4 bottom-4 h-28 w-auto opacity-[0.12] brightness-0 invert sm:h-36" />
        <div className="relative grid gap-8 lg:grid-cols-[1.35fr_1fr] lg:items-end">
          <div>
            <div className="mb-5 inline-flex items-center gap-3 rounded-2xl border border-white/20 bg-white/95 px-4 py-2.5 shadow-soft">
              <BrandLogo size="lg" href={null} className="h-10 w-auto sm:h-12" />
            </div>
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-white/70">
              {brand.name} · Institutional desk
            </p>
            <h1 className="mt-3 max-w-xl font-[family-name:var(--font-display)] text-3xl font-semibold tracking-tight sm:text-5xl text-balance">
              {brand.name} property intelligence.
            </h1>
            <p className="mt-4 max-w-lg text-[15px] leading-relaxed text-white/80">
              Monitor holdings, surface opportunities, and operate the {brand.name} real-estate
              book with institutional clarity.
            </p>
            <div className="mt-7 flex flex-wrap gap-3">
              <Link
                href="/properties/new"
                className="inline-flex h-11 items-center gap-2 rounded-2xl bg-white px-5 text-[13px] font-semibold text-[#0B4C84] shadow-soft transition hover:scale-[1.02]"
              >
                <Plus className="h-4 w-4" />
                New asset
              </Link>
              <Link
                href="/properties"
                className="inline-flex h-11 items-center gap-2 rounded-2xl border border-white/25 bg-white/10 px-5 text-[13px] font-semibold text-white backdrop-blur transition hover:bg-white/15"
              >
                Open portfolio
                <ArrowUpRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between rounded-2xl border border-white/15 bg-white/10 px-4 py-3 backdrop-blur-md">
              <span className="text-[11px] uppercase tracking-wider text-white/65">{brand.legal}</span>
              <BrandLogo size="xs" href={null} invert className="h-4 w-auto opacity-90" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: "Total assets", value: statistics?.total_properties ?? 0 },
                { label: "Active", value: statistics?.active_properties ?? 0 },
                { label: "Drafts", value: statistics?.draft_properties ?? 0 },
                {
                  label: "Closed",
                  value: (statistics?.sold_properties ?? 0) + (statistics?.rented_properties ?? 0),
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-2xl border border-white/15 bg-white/10 p-4 backdrop-blur-md"
                >
                  <p className="text-[11px] uppercase tracking-wider text-white/65">{item.label}</p>
                  <p className="mt-1 font-[family-name:var(--font-display)] text-2xl font-semibold tabular-nums">
                    {item.value}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </MotionDiv>

      {/* KPI strip */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          index={0}
          title="Total properties"
          value={statistics?.total_properties ?? 0}
          icon={<Building2 className="h-5 w-5" strokeWidth={1.75} />}
          description="Entire book"
          trend={{ value: "Live", positive: true }}
        />
        <StatCard
          index={1}
          title="Active listings"
          value={statistics?.active_properties ?? 0}
          icon={<CheckCircle2 className="h-5 w-5" strokeWidth={1.75} />}
          description="Market ready"
          accent="green"
          trend={{ value: "+ready", positive: true }}
        />
        <StatCard
          index={2}
          title="In draft"
          value={statistics?.draft_properties ?? 0}
          icon={<Clock className="h-5 w-5" strokeWidth={1.75} />}
          description="Awaiting publish"
          accent="neutral"
        />
        <StatCard
          index={3}
          title="Sold / Rented"
          value={(statistics?.sold_properties ?? 0) + (statistics?.rented_properties ?? 0)}
          icon={<FileCheck2 className="h-5 w-5" strokeWidth={1.75} />}
          description="Completed deals"
          accent="navy"
        />
      </div>

      {/* Quick actions */}
      <MotionDiv
        variants={staggerContainer}
        initial="hidden"
        animate="show"
        className="grid gap-4 md:grid-cols-3"
      >
        {quickActions.map((action) => (
          <MotionDiv key={action.href} variants={listItem}>
            <Link
              href={action.href}
              className="group flex items-start gap-4 rounded-2xl border border-border/80 bg-white p-5 shadow-soft transition hover:-translate-y-0.5 hover:shadow-lift"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent text-primary transition group-hover:scale-105">
                <action.icon className="h-5 w-5" strokeWidth={1.75} />
              </span>
              <div className="flex-1">
                <div className="flex items-center justify-between gap-2">
                  <p className="font-semibold tracking-tight">{action.title}</p>
                  <ArrowUpRight className="h-4 w-4 text-muted-foreground transition group-hover:text-primary" />
                </div>
                <p className="mt-1 text-[13px] text-muted-foreground">{action.desc}</p>
              </div>
            </Link>
          </MotionDiv>
        ))}
      </MotionDiv>

      {/* Charts + insight */}
      <div className="grid gap-4 lg:grid-cols-2">
        <MotionDiv
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="rounded-3xl border border-border/80 bg-white p-6 shadow-soft"
        >
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-primary">
                Composition
              </p>
              <h2 className="font-[family-name:var(--font-display)] text-xl font-semibold tracking-tight">
                Assets by type
              </h2>
            </div>
            <TrendingUp className="h-5 w-5 text-primary" />
          </div>
          <div className="h-72">
            {typeData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                No distribution data yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={typeData} barSize={28}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#DCE5EA" vertical={false} />
                  <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#66788A" }} axisLine={false} tickLine={false} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#66788A" }} axisLine={false} tickLine={false} />
                  <Tooltip
                    cursor={{ fill: "#EEF3F5" }}
                    contentStyle={{
                      borderRadius: 16,
                      border: "1px solid #DCE5EA",
                      boxShadow: "0 8px 24px rgba(22,33,43,0.08)",
                    }}
                  />
                  <Bar dataKey="value" radius={[10, 10, 4, 4]} fill="#0C8A43" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </MotionDiv>

        <MotionDiv
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="rounded-3xl border border-border/80 bg-white p-6 shadow-soft"
        >
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-primary">
                Lifecycle
              </p>
              <h2 className="font-[family-name:var(--font-display)] text-xl font-semibold tracking-tight">
                Status mix
              </h2>
            </div>
            <Sparkles className="h-5 w-5 text-[#0B4C84]" />
          </div>
          <div className="h-72">
            {statusData.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                No status data yet
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={58}
                    outerRadius={88}
                    paddingAngle={3}
                    stroke="#fff"
                    strokeWidth={3}
                  >
                    {statusData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={CHART[index % CHART.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      borderRadius: 16,
                      border: "1px solid #DCE5EA",
                      boxShadow: "0 8px 24px rgba(22,33,43,0.08)",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </MotionDiv>
      </div>
    </div>
  );
}
