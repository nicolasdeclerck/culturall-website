'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { Article } from '../../types/article';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ArticleDetailPage() {
  const params = useParams<{ slug: string }>();
  const searchParams = useSearchParams();
  const previewToken = searchParams.get('preview_token');

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!params.slug) return;
    const controller = new AbortController();

    const url = previewToken
      ? `${API_URL}/api/preview/article/?token=${encodeURIComponent(previewToken)}`
      : `${API_URL}/api/blog/articles/${encodeURIComponent(params.slug)}/`;

    fetch(url, {
      credentials: 'include',
      signal: controller.signal,
    })
      .then((res) => {
        if (res.status === 404) return null;
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        setArticle(data ?? null);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setArticle(null);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [params.slug, previewToken]);

  if (loading) {
    return (
      <div className="page blog-page">
        <p className="blog-page__message">Chargement…</p>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="page blog-page">
        <div className="article-detail-wrapper">
          <Link href="/blog" className="article-detail__back">
            <span className="article-detail__back-icon" aria-hidden="true">←</span>
            <span>Blog</span>
          </Link>
          <h1>Article introuvable</h1>
          <p>Cet article n&apos;existe pas ou a été retiré.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page blog-page">
      {previewToken && (
        <div className="preview-banner" role="status">
          <span>Mode aperçu — ce contenu n&apos;est pas encore publié</span>
          <Link href={`/blog/${params.slug}`} className="preview-banner__exit">
            Quitter l&apos;aperçu
          </Link>
        </div>
      )}
      <div className="article-detail-wrapper">
        <Link href="/blog" className="article-detail__back">
          <span className="article-detail__back-icon" aria-hidden="true">←</span>
          <span>Blog</span>
        </Link>
        <article className="article-detail">
          <h1>{article.title}</h1>
          {article.tags.length > 0 && (
            <div className="article-detail__byline">
              {article.tags.map((tag, i) => (
                <span key={`tag-${i}`} className="article-detail__byline-item">{tag}</span>
              ))}
            </div>
          )}
          {article.illustration_url && (
            <img
              src={article.illustration_url}
              alt=""
              className="article-detail__illustration"
            />
          )}
          {article.summary && (
            <p className="article-detail__summary">{article.summary}</p>
          )}
          <div
            className="content-overlay__body"
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
        </article>
      </div>
    </div>
  );
}
