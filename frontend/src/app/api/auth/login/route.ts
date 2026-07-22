import { NextResponse } from "next/server";
import { findDemoUser, mintSessionToken } from "@/lib/auth/server";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const email = String(body.email || "");
    const password = String(body.password || "");

    if (!email || !password) {
      return NextResponse.json(
        { error: { code: "validation", message: "Email and password are required" } },
        { status: 400 }
      );
    }

    const user = findDemoUser(email, password);
    if (!user) {
      return NextResponse.json(
        { error: { code: "unauthorized", message: "Invalid email or password" } },
        { status: 401 }
      );
    }

    const session = await mintSessionToken(user);
    return NextResponse.json({ data: session });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Login failed";
    return NextResponse.json(
      { error: { code: "server_error", message } },
      { status: 500 }
    );
  }
}
