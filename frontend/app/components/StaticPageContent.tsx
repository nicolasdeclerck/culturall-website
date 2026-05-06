import Link from 'next/link';

const API_URL =
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  '';

type StaticPage = {
  slug: string;
  title: string;
  body: string;
};

async function fetchStaticPage(
  slug: string,
  previewToken?: string,
): Promise<StaticPage | null> {
  if (!API_URL) return null;
  const url = previewToken
    ? `${API_URL}/api/preview/page/?token=${encodeURIComponent(previewToken)}`
    : `${API_URL}/api/pages/${slug}/`;
  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return null;
    return (await res.json()) as StaticPage;
  } catch {
    return null;
  }
}

type Props = {
  slug: string;
  fallbackTitle: string;
  previewToken?: string;
};

export default async function StaticPageContent({
  slug,
  fallbackTitle,
  previewToken,
}: Props) {
  const page = await fetchStaticPage(slug, previewToken);

  return (
    <main className="page">
      {previewToken && (
        <div className="preview-banner" role="status">
          <span>Mode aperçu — ce contenu n&apos;est pas encore publié</span>
          <Link href={`/${slug}`} className="preview-banner__exit">
            Quitter l&apos;aperçu
          </Link>
        </div>
      )}
      <div className="static-page-wrapper">
        <h1>{page?.title ?? fallbackTitle}</h1>
        {page?.body && (
          <div dangerouslySetInnerHTML={{ __html: page.body }} />
        )}
      </div>
    </main>
  );
}
