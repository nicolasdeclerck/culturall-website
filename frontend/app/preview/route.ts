import { NextRequest, NextResponse } from 'next/server';

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://django:8000';

// Dispatch table : content_type → endpoint backend draft + préfixe de route frontend
const PREVIEW_ROUTES: Record<string, { backendPath: string; frontendPrefix: string }> = {
  'blog.articlepage': {
    backendPath: '/api/preview/article/',
    frontendPrefix: '/blog',
  },
  'projects.projectpage': {
    backendPath: '/api/preview/project/',
    frontendPrefix: '/projets',
  },
};

/**
 * Reconstruit l'URL externe de la requête à partir des headers X-Forwarded-*
 * (posés par Traefik en prod). Sans ça, request.url retombe sur l'adresse
 * interne du container (0.0.0.0:3000), ce qui casse les redirections en prod.
 */
function getExternalBaseUrl(request: NextRequest): string {
  const host = request.headers.get('x-forwarded-host') || request.headers.get('host');
  const proto = request.headers.get('x-forwarded-proto') || 'https';
  if (host) return `${proto}://${host}`;
  return request.nextUrl.origin;
}

export async function GET(request: NextRequest) {
  const { searchParams } = request.nextUrl;
  const token = searchParams.get('token');
  const contentType = searchParams.get('content_type');

  if (!token) {
    return NextResponse.json({ error: 'Token manquant' }, { status: 400 });
  }

  if (!contentType || !(contentType in PREVIEW_ROUTES)) {
    return NextResponse.json({ error: 'content_type non supporté' }, { status: 400 });
  }

  const { backendPath, frontendPrefix } = PREVIEW_ROUTES[contentType];

  let res: Response;
  try {
    res = await fetch(
      `${INTERNAL_API_URL}${backendPath}?token=${encodeURIComponent(token)}`,
      { cache: 'no-store' },
    );
  } catch {
    return NextResponse.json({ error: 'Backend inaccessible' }, { status: 502 });
  }

  if (!res.ok) {
    return NextResponse.json({ error: 'Token invalide ou expiré' }, { status: 404 });
  }

  const data = await res.json();
  const slug: string = data.slug;

  const previewUrl = new URL(`${frontendPrefix}/${slug}`, getExternalBaseUrl(request));
  previewUrl.searchParams.set('preview_token', token);
  previewUrl.searchParams.set('content_type', contentType);

  return NextResponse.redirect(previewUrl);
}
