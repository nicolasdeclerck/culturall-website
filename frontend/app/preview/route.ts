import { NextRequest, NextResponse } from 'next/server';

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://django:8000';

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

  if (!token) {
    return NextResponse.json({ error: 'Token manquant' }, { status: 400 });
  }

  // Valide le token et récupère les données brouillon (dont le slug)
  let res: Response;
  try {
    res = await fetch(
      `${INTERNAL_API_URL}/api/preview/draft/?token=${encodeURIComponent(token)}`,
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

  // Redirige vers la page article avec le token en query param
  // Le token fait office de credential — la page client l'utilise pour fetcher le brouillon
  const previewUrl = new URL(`/blog/${slug}`, getExternalBaseUrl(request));
  previewUrl.searchParams.set('preview_token', token);

  return NextResponse.redirect(previewUrl);
}
