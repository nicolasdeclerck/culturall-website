import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Mentions légales',
};

const API_URL =
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  '';

const FALLBACK_TITLE = 'Mentions légales';

type StaticPage = {
  slug: string;
  title: string;
  body: string;
};

async function fetchStaticPage(slug: string): Promise<StaticPage | null> {
  if (!API_URL) return null;
  try {
    const res = await fetch(`${API_URL}/api/pages/${slug}/`, {
      cache: 'no-store',
    });
    if (!res.ok) return null;
    return (await res.json()) as StaticPage;
  } catch {
    return null;
  }
}

export default async function MentionsLegales() {
  const page = await fetchStaticPage('mentions-legales');

  return (
    <main className="page">
      <h1>{page?.title ?? FALLBACK_TITLE}</h1>
      {page?.body && (
        <div dangerouslySetInnerHTML={{ __html: page.body }} />
      )}
    </main>
  );
}
