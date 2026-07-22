export type AuthRole =
  | "platform_admin"
  | "tenant_admin"
  | "property_manager"
  | "property_viewer"
  | "partner_readonly"
  | "api_integration";

export const ALL_PERMISSIONS = [
  "property:create",
  "property:read",
  "property:update",
  "property:delete",
  "property:search",
  "property:bulk_import",
  "property:bulk_update",
  "property:bulk_delete",
  "property:manage_media",
  "property:verify_documents",
  "property:manage_ownership",
  "property:audit",
  "property:statistics",
  "property:partner_read",
] as const;

export type Permission = (typeof ALL_PERMISSIONS)[number];

export const ROLE_PERMISSIONS: Record<AuthRole, readonly Permission[]> = {
  platform_admin: ALL_PERMISSIONS,
  tenant_admin: ALL_PERMISSIONS,
  property_manager: [
    "property:create",
    "property:read",
    "property:update",
    "property:delete",
    "property:search",
    "property:bulk_import",
    "property:manage_media",
    "property:verify_documents",
    "property:manage_ownership",
    "property:statistics",
  ],
  property_viewer: ["property:read", "property:search", "property:statistics"],
  partner_readonly: ["property:partner_read", "property:search"],
  api_integration: ["property:read", "property:search"],
};

export const DEV_TENANT_ID = "00000000-0000-0000-0000-000000000010";

export interface DemoUser {
  email: string;
  password: string;
  name: string;
  userId: string;
  role: AuthRole;
  tenantId: string;
}

/** Demo accounts for local / staging until Identity Service is wired */
export const DEMO_USERS: DemoUser[] = [
  {
    email: "admin@torkam.com",
    password: "admin123",
    name: "Torkam Admin",
    userId: "00000000-0000-0000-0000-000000000001",
    role: "tenant_admin",
    tenantId: DEV_TENANT_ID,
  },
  {
    email: "manager@torkam.com",
    password: "manager123",
    name: "Portfolio Manager",
    userId: "00000000-0000-0000-0000-000000000002",
    role: "property_manager",
    tenantId: DEV_TENANT_ID,
  },
  {
    email: "viewer@torkam.com",
    password: "viewer123",
    name: "Read-only Viewer",
    userId: "00000000-0000-0000-0000-000000000003",
    role: "property_viewer",
    tenantId: DEV_TENANT_ID,
  },
];

export interface AuthSession {
  token: string;
  email: string;
  name: string;
  userId: string;
  tenantId: string;
  role: AuthRole;
  permissions: Permission[];
  expiresAt: number;
}

export const AUTH_STORAGE_KEY = "torkam.auth.session";
