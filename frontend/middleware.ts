import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const middleware = (request: NextRequest) => {
  const authToken = request.cookies.get("auth_token");

  if (!authToken) {
    console.log("No auth token found");
    return NextResponse.redirect(new URL("/auth", request.url));
  }
  return NextResponse.next();
};

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - auth (auth routes)
     */
    "/((?!api|_next/static|_next/image|favicon.ico|auth).*)",
  ],
};

export default middleware;
