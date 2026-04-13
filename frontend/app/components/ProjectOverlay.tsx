'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

export interface Project {
  id: number;
  title: string;
  description: string;
  youtube_url: string;
  tags: string[];
  thumbnail_url: string | null;
}

interface ProjectOverlayProps {
  project: Project | null;
  onClose: () => void;
}

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?.*v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})/,
  );
  return match ? match[1] : null;
}

export default function ProjectOverlay({ project, onClose }: ProjectOverlayProps) {
  const [visible, setVisible] = useState(false);
  const rafRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleClose = useCallback(() => {
    setVisible(false);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClose, 400);
  }, [onClose]);

  useEffect(() => {
    if (project) {
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
  }, [project]);

  useEffect(() => {
    if (!project) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') handleClose();
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [project, handleClose]);

  function handleBackdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) handleClose();
  }

  if (!project) return null;

  const videoId = extractYouTubeId(project.youtube_url);

  return (
    <div
      className={`article-overlay ${visible ? 'article-overlay--visible' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-overlay-title"
      onClick={handleBackdropClick}
    >
      <button className="article-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>
      <div className="article-overlay__content">
        <h2 id="project-overlay-title" className="article-overlay__title">{project.title}</h2>
        {project.tags.length > 0 && (
          <div className="article-overlay__tags">
            {project.tags.map((tag, i) => (
              <span key={`${tag}-${i}`} className="article-overlay__tag">{tag}</span>
            ))}
          </div>
        )}
        <div
          className="article-overlay__body"
          dangerouslySetInnerHTML={{ __html: project.description }}
        />
        {videoId && (
          <div className="project-overlay__video">
            <iframe
              src={`https://www.youtube.com/embed/${videoId}`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
              sandbox="allow-scripts allow-same-origin allow-presentation allow-popups"
              loading="lazy"
              allowFullScreen
              title={project.title}
            />
          </div>
        )}
      </div>
    </div>
  );
}
