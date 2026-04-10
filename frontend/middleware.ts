import { NextRequest, NextResponse } from 'next/server';

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://django:8000';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Never redirect on the login page, static assets, or Next.js internals
  if (
    pathname === '/login' ||
    pathname.startsWith('/_next/') ||
    pathname.startsWith('/api/') ||
    pathname.includes('.')
  ) {
    return NextResponse.next();
  }

  // Forward cookies to Django so it can validate the session
  const cookieHeader = request.headers.get('cookie') || '';

  try {
    const res = await fetch(`${INTERNAL_API_URL}/api/auth/check/`, {
      headers: { cookie: cookieHeader },
    });

    if (!res.ok) {
      // If Django is unreachable, allow the request through
      return NextResponse.next();
    }

    const data = await res.json();

    if (data.require_authentication && !data.authenticated) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('next', pathname);
      return NextResponse.redirect(loginUrl);
    }
  } catch {
    // If the API call fails, allow the request through
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
};
