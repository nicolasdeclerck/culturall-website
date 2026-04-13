'use client';

import { useOverlay } from '../hooks/useOverlay';

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
  const { visible, handleClose, handleBackdropClick } = useOverlay(!!article, onClose);

  if (!article) return null;

  return (
    <div
      className={`content-overlay ${visible ? 'content-overlay--visible' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="article-overlay-title"
      onClick={handleBackdropClick}
    >
      <button className="content-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>
      <div className="content-overlay__content">
        {article.illustration_url && (
          <img
            src={article.illustration_url}
            alt=""
            className="content-overlay__illustration"
          />
        )}
        <h2 id="article-overlay-title" className="content-overlay__title">{article.title}</h2>
        {article.tags.length > 0 && (
          <div className="content-overlay__tags">
            {article.tags.map((tag, i) => (
              <span key={`${tag}-${i}`} className="content-overlay__tag">{tag}</span>
            ))}
          </div>
        )}
        {article.summary && (
          <p className="content-overlay__summary">{article.summary}</p>
        )}
        <div
          className="content-overlay__body"
          dangerouslySetInnerHTML={{ __html: article.content }}
        />
      </div>
    </div>
  );
}
