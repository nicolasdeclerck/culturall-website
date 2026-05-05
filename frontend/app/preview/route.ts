import { NextRequest, NextResponse } from 'next/server';

const INTERNAL_API_URL =
  process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://django:8000';

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
  const previewUrl = new URL(`/blog/${slug}`, request.url);
  previewUrl.searchParams.set('preview_token', token);

  return NextResponse.redirect(previewUrl);
}
