import { SignJWT } from "jose";
import {
  DEMO_USERS,
  ROLE_PERMISSIONS,
  type AuthSession,
  type DemoUser,
  type Permission,
} from "./types";

const DEFAULT_SECRET = "dev-secret-change-in-production";

function getSecret() {
  return new TextEncoder().encode(
    process.env.JWT_SECRET || process.env.NEXT_PUBLIC_JWT_SECRET || DEFAULT_SECRET
  );
}

export function findDemoUser(email: string, password: string): DemoUser | null {
  const normalized = email.trim().toLowerCase();
  return (
    DEMO_USERS.find(
      (u) => u.email === normalized && u.password === password
    ) ?? null
  );
}

export async function mintSessionToken(user: DemoUser): Promise<AuthSession> {
  const permissions = [...ROLE_PERMISSIONS[user.role]] as Permission[];
  const expiresIn = "12h";
  const expiresAt = Date.now() + 12 * 60 * 60 * 1000;

  const token = await new SignJWT({
    tenant_id: user.tenantId,
    roles: [user.role],
    permissions,
    name: user.name,
    email: user.email,
  })
    .setProtectedHeader({ alg: "HS256", typ: "JWT" })
    .setSubject(user.userId)
    .setAudience("property-service")
    .setIssuedAt()
    .setExpirationTime(expiresIn)
    .sign(getSecret());

  return {
    token,
    email: user.email,
    name: user.name,
    userId: user.userId,
    tenantId: user.tenantId,
    role: user.role,
    permissions,
    expiresAt,
  };
}
