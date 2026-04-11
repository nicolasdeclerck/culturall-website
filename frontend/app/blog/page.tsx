'use client';

import { useEffect, useMemo, useState } from 'react';
import ArticleOverlay, { Article } from '../components/ArticleOverlay';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
const EXCERPT_LENGTH = 500;

function stripHtml(html: string): string {
  return html.replace(/<[^>]*>/g, '');
}

export default function BlogPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<Article | null>(null);

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
        if (Array.isArray(data)) setArticles(data);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setArticles([]);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  const allTags = Array.from(new Set(articles.flatMap((a) => a.tags))).sort();
  const filtered = selectedTag
    ? articles.filter((a) => a.tags.includes(selectedTag))
    : articles;

  const excerpts = useMemo(() => {
    const map = new Map<number, string>();
    for (const a of articles) {
      map.set(a.id, stripHtml(a.content));
    }
    return map;
  }, [articles]);

  return (
    <div className="page blog-page">
      <h1>Blog</h1>

      {allTags.length > 0 && (
        <div className="blog-filters">
          <button
            className={`blog-filters__btn${selectedTag === null ? ' blog-filters__btn--active' : ''}`}
            onClick={() => setSelectedTag(null)}
          >
            Tous
          </button>
          {allTags.map((tag) => (
            <button
              key={tag}
              className={`blog-filters__btn${selectedTag === tag ? ' blog-filters__btn--active' : ''}`}
              onClick={() => setSelectedTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      )}

      {loading ? (
        <p className="blog-page__message">Chargement…</p>
      ) : filtered.length === 0 ? (
        <p className="blog-page__message">Aucun article pour le moment.</p>
      ) : (
        <div className="blog-masonry">
          {filtered.map((article) => {
            const text = excerpts.get(article.id) ?? '';
            return (
              <button
                key={article.id}
                className="blog-card"
                onClick={() => setSelectedArticle(article)}
              >
                {article.illustration_url && (
                  <img
                    src={article.illustration_url}
                    alt=""
                    className="blog-card__image"
                  />
                )}
                <div className="blog-card__text">
                  <h3 className="blog-card__title">{article.title}</h3>
                  <p className="blog-card__excerpt">
                    {text.slice(0, EXCERPT_LENGTH)}
                    {text.length > EXCERPT_LENGTH ? '…' : ''}
                  </p>
                </div>
              </button>
            );
          })}
        </div>
      )}

      <ArticleOverlay article={selectedArticle} onClose={() => setSelectedArticle(null)} />
    </div>
  );
}
