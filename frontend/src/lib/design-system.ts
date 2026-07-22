/** Torkam design tokens — single source of truth from brand logo */

export const brand = {
  name: "Torkam",
  tagline: "Property Intelligence",
  logo: "/torkam-logo.svg",
  legal: "Torkam Holding",
} as const;

export const colors = {
  primary: "#0C8A43",
  secondary: "#2E9E67",
  navy: "#0B4C84",
  navyDeep: "#124775",
  background: "#F8FAFC",
  surface: "#FFFFFF",
  surface2: "#EEF3F5",
  border: "#DCE5EA",
  text: "#16212B",
  textMuted: "#66788A",
  success: "#1FA971",
  warning: "#E8B949",
  error: "#D9485A",
} as const;

export const space = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  "2xl": 24,
  "3xl": 32,
  "4xl": 40,
  "5xl": 48,
  "6xl": 64,
} as const;

export const radius = {
  sm: 12,
  md: 16,
  lg: 20,
  xl: 24,
  full: 9999,
} as const;

export const motion = {
  fast: 0.18,
  base: 0.28,
  slow: 0.45,
  spring: { type: "spring" as const, stiffness: 380, damping: 28 },
  softSpring: { type: "spring" as const, stiffness: 260, damping: 24 },
  ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
};

export const statusTone: Record<string, { bg: string; fg: string; ring: string }> = {
  draft: { bg: "#EEF3F5", fg: "#66788A", ring: "#DCE5EA" },
  pending_review: { bg: "#FFF8E8", fg: "#A67C00", ring: "#E8B949" },
  active: { bg: "#E8F6EE", fg: "#0C8A43", ring: "#2E9E67" },
  paused: { bg: "#EEF3F5", fg: "#66788A", ring: "#DCE5EA" },
  sold: { bg: "#E8F0F8", fg: "#0B4C84", ring: "#0B4C84" },
  rented: { bg: "#E8F0F8", fg: "#0B4C84", ring: "#124775" },
  archived: { bg: "#F3F4F6", fg: "#66788A", ring: "#DCE5EA" },
  deleted: { bg: "#FDECEE", fg: "#D9485A", ring: "#D9485A" },
};
