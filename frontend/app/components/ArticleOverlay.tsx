'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface Article {
  id: number;
  title: string;
  summary: string;
  content: string;
  illustration_url: string | null;
  tags: string[];
  created_at: string;
}

interface ArticleOverlayProps {
  article: Article | null;
  onClose: () => void;
}

export default function ArticleOverlay({ article, onClose }: ArticleOverlayProps) {
  const [visible, setVisible] = useState(false);
  const rafRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleClose = useCallback(() => {
    setVisible(false);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClose, 400);
  }, [onClose]);

  useEffect(() => {
    if (article) {
      rafRef.current = requestAnimationFrame(() => setVisible(true));
      document.body.style.overflow = 'hidden';
      return () => {
        cancelAnimationFrame(rafRef.current);
        clearTimeout(timeoutRef.current);
        document.body.style.overflow = '';
      };
    } else {
      setVisible(false);
      document.body.style.overflow = '';
    }
  }, [article]);

  useEffect(() => {
    if (!article) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') handleClose();
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [article, handleClose]);

  function handleBackdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) handleClose();
  }

  if (!article) return null;

  return (
    <div
      className={`article-overlay ${visible ? 'article-overlay--visible' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="article-overlay-title"
      onClick={handleBackdropClick}
    >
      <button className="article-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>
      <div className="article-overlay__content">
        {article.illustration_url && (
          <img
            src={article.illustration_url}
            alt=""
            className="article-overlay__illustration"
          />
        )}
        <h2 id="article-overlay-title" className="article-overlay__title">{article.title}</h2>
        {article.tags.length > 0 && (
          <div className="article-overlay__tags">
            {article.tags.map((tag, i) => (
              <span key={`${tag}-${i}`} className="article-overlay__tag">{tag}</span>
            ))}
          </div>
        )}
        {article.summary && (
          <p className="article-overlay__summary">{article.summary}</p>
        )}
        <div
          className="article-overlay__body"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />
      </div>
    </div>
  );
}
