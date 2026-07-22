"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff, Lock, Mail, ShieldCheck } from "lucide-react";
import { BrandLogo } from "@/components/ui-custom/brand-logo";
import { brand } from "@/lib/design-system";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MotionDiv } from "@/lib/motion";
import { DEMO_USERS } from "@/lib/auth/types";
import { roleLabel } from "@/lib/auth/session";

export default function LoginForm() {
  const { login, isAuthenticated, loading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") || "/";

  const [email, setEmail] = useState("admin@torkam.com");
  const [password, setPassword] = useState("admin123");
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && isAuthenticated) {
      router.replace(next);
    }
  }, [loading, isAuthenticated, router, next]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email, password);
      toast.success("Welcome to Torkam");
      router.replace(next);
    } catch (err) {
      toast.error("Sign-in failed", {
        description: err instanceof Error ? err.message : "Invalid credentials",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="relative flex min-h-dvh items-center justify-center overflow-hidden px-4 py-10">
      <div className="pointer-events-none absolute inset-0 gradient-hero opacity-[0.12]" />
      <div className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-primary/15 blur-3xl" />
      <div className="pointer-events-none absolute -right-16 bottom-0 h-80 w-80 rounded-full bg-navy/15 blur-3xl" />

      <MotionDiv
        initial={{ opacity: 0, y: 18 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="relative grid w-full max-w-5xl overflow-hidden rounded-[28px] border border-border/80 bg-white shadow-lift lg:grid-cols-[1.05fr_0.95fr]"
      >
        <div className="relative hidden gradient-hero p-10 text-white lg:flex lg:flex-col lg:justify-between">
          <div>
            <div className="inline-flex rounded-2xl bg-white px-4 py-2.5 shadow-soft">
              <BrandLogo size="lg" href={null} />
            </div>
            <h1 className="mt-10 font-[family-name:var(--font-display)] text-4xl font-semibold tracking-tight text-balance">
              {brand.name} secure access
            </h1>
            <p className="mt-4 max-w-sm text-[15px] leading-relaxed text-white/80">
              Sign in to the institutional property desk. Sessions are issued as platform JWTs
              and authorized by role permissions.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-[13px] text-white/85">
              <ShieldCheck className="h-4 w-4" />
              RBAC · tenant scoped · HS256 JWT
            </div>
            <p className="text-[11px] uppercase tracking-[0.16em] text-white/55">{brand.legal}</p>
          </div>
        </div>

        <div className="p-6 sm:p-10">
          <div className="mb-8 flex items-center justify-between gap-3 lg:hidden">
            <BrandLogo size="md" href={null} />
            <span className="text-[11px] font-semibold uppercase tracking-[0.14em] text-primary">
              Sign in
            </span>
          </div>

          <div className="mb-6 hidden lg:block">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary">Authorization</p>
            <h2 className="mt-1 font-[family-name:var(--font-display)] text-2xl font-semibold tracking-tight">
              Sign in to continue
            </h2>
          </div>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="username"
                  required
                  className="h-11 rounded-xl pl-9"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  required
                  className="h-11 rounded-xl pl-9 pr-10"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <button
                  type="button"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button type="submit" disabled={submitting} className="h-11 w-full rounded-2xl shadow-glow">
              {submitting ? "Signing in…" : "Sign in"}
            </Button>
          </form>

          <div className="mt-8 space-y-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Demo accounts
            </p>
            <div className="space-y-2">
              {DEMO_USERS.map((user) => (
                <button
                  key={user.email}
                  type="button"
                  onClick={() => {
                    setEmail(user.email);
                    setPassword(user.password);
                  }}
                  className="flex w-full items-center justify-between rounded-2xl border border-border bg-secondary/40 px-3.5 py-3 text-left transition hover:border-primary/30 hover:bg-accent/60"
                >
                  <div>
                    <p className="text-[13px] font-semibold">{user.name}</p>
                    <p className="text-[12px] text-muted-foreground">{user.email}</p>
                  </div>
                  <span className="rounded-full bg-white px-2.5 py-1 text-[10px] font-semibold text-primary shadow-soft">
                    {roleLabel(user.role)}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </MotionDiv>
    </div>
  );
}
