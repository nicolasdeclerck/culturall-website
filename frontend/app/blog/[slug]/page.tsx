'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Article } from '../../types/article';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ArticleDetailPage() {
  const params = useParams<{ id: string }>();
  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/api/blog/articles/`, {
      credentials: 'include',
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) {
          const match = data.find((a: Article) => String(a.id) === params.id) || null;
          setArticle(match);
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setArticle(null);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [params.id]);

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
