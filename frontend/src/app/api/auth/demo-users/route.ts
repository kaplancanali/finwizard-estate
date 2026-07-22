import { NextResponse } from "next/server";
import { DEMO_USERS, ROLE_PERMISSIONS } from "@/lib/auth/types";

/** Public demo account hints (no passwords) for the login screen */
export async function GET() {
  return NextResponse.json({
    data: DEMO_USERS.map((u) => ({
      email: u.email,
      name: u.name,
      role: u.role,
      permissions: ROLE_PERMISSIONS[u.role],
    })),
  });
}
