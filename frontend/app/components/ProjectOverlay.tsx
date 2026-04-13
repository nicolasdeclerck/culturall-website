'use client';

import { useOverlay } from '../hooks/useOverlay';

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
  const { visible, handleClose, handleBackdropClick } = useOverlay(!!project, onClose);

  if (!project) return null;

  const videoId = extractYouTubeId(project.youtube_url);

  return (
    <div
      className={`content-overlay ${visible ? 'content-overlay--visible' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="project-overlay-title"
      onClick={handleBackdropClick}
    >
      <button className="content-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>
      <div className="content-overlay__content">
        <h2 id="project-overlay-title" className="content-overlay__title">{project.title}</h2>
        {project.tags.length > 0 && (
          <div className="content-overlay__tags">
            {project.tags.map((tag, i) => (
              <span key={`${tag}-${i}`} className="content-overlay__tag">{tag}</span>
            ))}
          </div>
        )}
        <div
          className="content-overlay__body"
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
