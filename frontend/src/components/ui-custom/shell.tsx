"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building2,
  LayoutDashboard,
  Search,
  Plus,
  Bell,
  Command,
  LogOut,
  Shield,
} from "lucide-react";
import { brand } from "@/lib/design-system";
import { BrandLogo } from "@/components/ui-custom/brand-logo";
import { cn } from "@/lib/utils";
import { MotionDiv, MotionHeader } from "@/lib/motion";
import { useAuth } from "@/components/auth/auth-provider";
import { roleLabel } from "@/lib/auth/session";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface ShellProps {
  children: React.ReactNode;
  className?: string;
}

const nav = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/properties", label: "Portfolio", icon: Building2 },
  { href: "/properties/search", label: "Discover", icon: Search },
];

export function Shell({ children, className }: ShellProps) {
  const pathname = usePathname();
  const { session, logout, can } = useAuth();
  const isLogin = pathname === "/login" || pathname.startsWith("/login/");

  if (isLogin) {
    return <>{children}</>;
  }

  return (
    <div className="relative min-h-dvh flex flex-col">
      <MotionHeader
        initial={{ y: -12, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
        className="sticky top-0 z-50 border-b border-border/70 glass-strong"
      >
        <div className="mx-auto flex h-[72px] w-full max-w-[1440px] items-center justify-between gap-6 px-5 lg:px-8">
          <div className="flex items-center gap-3 shrink-0">
            <BrandLogo size="md" priority className="h-9 w-auto sm:h-10" />
            <div className="hidden sm:block leading-tight border-l border-border pl-3">
              <p className="font-[family-name:var(--font-display)] text-[14px] font-semibold tracking-tight text-foreground">
                {brand.name}
              </p>
              <p className="text-[11px] text-muted-foreground tracking-wide">
                {brand.tagline}
              </p>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-1 rounded-2xl border border-border/80 bg-white/70 p-1 shadow-soft">
            {nav.map((item) => {
              const active =
                item.href === "/"
                  ? pathname === "/"
                  : pathname === item.href ||
                    (item.href === "/properties" &&
                      pathname.startsWith("/properties") &&
                      !pathname.startsWith("/properties/search") &&
                      pathname !== "/properties/search");
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "relative flex items-center gap-2 rounded-xl px-3.5 py-2 text-[13px] font-medium transition-colors",
                    active
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  {active && (
                    <MotionDiv
                      layoutId="nav-pill"
                      className="absolute inset-0 rounded-xl bg-accent shadow-soft"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                  <Icon className="relative z-10 h-4 w-4" strokeWidth={1.75} />
                  <span className="relative z-10">{item.label}</span>
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-2">
            <button
              type="button"
              className="hidden lg:flex h-10 items-center gap-2 rounded-xl border border-border bg-white/80 px-3 text-[12px] text-muted-foreground shadow-soft transition hover:border-primary/30 hover:text-foreground"
            >
              <Command className="h-3.5 w-3.5" />
              <span>Search</span>
              <kbd className="ml-2 rounded-md bg-secondary px-1.5 py-0.5 text-[10px] font-medium">⌘K</kbd>
            </button>
            <button
              type="button"
              className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-white/80 text-muted-foreground shadow-soft transition hover:text-foreground"
              aria-label="Notifications"
            >
              <Bell className="h-4 w-4" strokeWidth={1.75} />
              <span className="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-primary" />
            </button>
            {can("property:create") && (
              <Link
                href="/properties/new"
                className="inline-flex h-10 items-center gap-1.5 rounded-xl bg-primary px-3.5 text-[13px] font-semibold text-primary-foreground shadow-glow transition hover:brightness-110 active:scale-[0.98]"
              >
                <Plus className="h-4 w-4" strokeWidth={2} />
                <span className="hidden sm:inline">New asset</span>
              </Link>
            )}

            <DropdownMenu>
              <DropdownMenuTrigger className="inline-flex h-10 items-center gap-2 rounded-xl border border-border bg-white/90 px-2.5 text-left shadow-soft outline-none">
                <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-[11px] font-bold text-primary">
                  {(session?.name || "T").slice(0, 1)}
                </span>
                <span className="hidden max-w-[120px] truncate text-[12px] font-medium sm:block">
                  {session?.name || "Account"}
                </span>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-64 rounded-2xl">
                <DropdownMenuLabel className="space-y-1">
                  <p className="text-sm font-semibold">{session?.name}</p>
                  <p className="text-xs font-normal text-muted-foreground">{session?.email}</p>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <div className="px-2 py-1.5 text-[11px] text-muted-foreground">
                  <div className="mb-1 flex items-center gap-1.5 font-medium text-foreground">
                    <Shield className="h-3.5 w-3.5 text-primary" />
                    {session ? roleLabel(session.role) : "—"}
                  </div>
                  <p className="truncate">Tenant · {session?.tenantId.slice(0, 8)}…</p>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={logout} className="cursor-pointer text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </MotionHeader>

      <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-border/80 glass-strong md:hidden pb-[env(safe-area-inset-bottom)]">
        <div className="mx-auto flex h-16 max-w-lg items-center justify-around px-2">
          {nav.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex flex-col items-center gap-1 rounded-xl px-4 py-2 text-[10px] font-medium transition",
                  active ? "text-primary" : "text-muted-foreground"
                )}
              >
                <span
                  className={cn(
                    "flex h-9 w-9 items-center justify-center rounded-xl transition",
                    active && "bg-accent shadow-soft"
                  )}
                >
                  <Icon className="h-5 w-5" strokeWidth={active ? 2 : 1.75} />
                </span>
                {item.label}
              </Link>
            );
          })}
          {can("property:create") ? (
            <Link
              href="/properties/new"
              className="flex flex-col items-center gap-1 rounded-xl px-4 py-2 text-[10px] font-medium text-primary"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-glow">
                <Plus className="h-5 w-5" strokeWidth={2} />
              </span>
              Create
            </Link>
          ) : (
            <button
              type="button"
              onClick={logout}
              className="flex flex-col items-center gap-1 rounded-xl px-4 py-2 text-[10px] font-medium text-muted-foreground"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-secondary">
                <LogOut className="h-5 w-5" strokeWidth={2} />
              </span>
              Out
            </button>
          )}
        </div>
      </nav>

      <main
        className={cn(
          "relative mx-auto w-full max-w-[1440px] flex-1 px-5 pb-24 pt-8 lg:px-8 lg:pb-12",
          className
        )}
      >
        {children}
      </main>

      <footer className="hidden border-t border-border/60 py-8 md:block">
        <div className="mx-auto flex max-w-[1440px] flex-col items-center gap-3 px-8 text-center">
          <BrandLogo size="sm" href="/" />
          <p className="text-[11px] text-muted-foreground">
            © {new Date().getFullYear()} {brand.legal} · {brand.name} Property Intelligence
          </p>
        </div>
      </footer>
    </div>
  );
}
