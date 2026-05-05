'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Article } from '../types/article';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function BlogCarousel() {
  const [articles, setArticles] = useState<Article[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/api/blog/articles/?limit=5`, {
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
      });
    return () => controller.abort();
  }, []);

  function scrollBy(direction: number) {
    if (!scrollRef.current) return;
    const cardWidth = scrollRef.current.querySelector('.carousel-card')?.clientWidth ?? 300;
    scrollRef.current.scrollBy({ left: direction * (cardWidth + 24), behavior: 'smooth' });
  }

  if (articles.length === 0) return null;

  return (
    <section className="blog-carousel-section">
      <h2 className="blog-carousel-section__title">Derniers Articles</h2>
      <div className="blog-carousel-wrapper">
        <button
          className="blog-carousel__arrow blog-carousel__arrow--left"
          onClick={() => scrollBy(-1)}
          aria-label="Article précédent"
        >
          ‹
        </button>
        <div className="blog-carousel" ref={scrollRef}>
          {articles.map((article) => (
            <Link
              key={article.id}
              href={`/blog/${article.slug}`}
              className="carousel-card"
            >
              {article.illustration_url ? (
                <img
                  src={article.illustration_url}
                  alt=""
                  className="carousel-card__image"
                />
              ) : (
                <div className="carousel-card__placeholder" />
              )}
              <span className="carousel-card__title">{article.title}</span>
            </Link>
          ))}
        </div>
        <button
          className="blog-carousel__arrow blog-carousel__arrow--right"
          onClick={() => scrollBy(1)}
          aria-label="Article suivant"
        >
          ›
        </button>
      </div>
      <Link href="/blog" className="blog-carousel-section__link">
        Voir tous les articles →
      </Link>
    </section>
  );
}
