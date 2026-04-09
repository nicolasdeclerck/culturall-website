'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface Project {
  id: number;
  title: string;
  description: string;
  youtube_url: string;
  tags: string[];
  thumbnail_url: string | null;
}

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?.*v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})/,
  );
  return match ? match[1] : null;
}

interface ProjectsOverlayProps {
  open: boolean;
  onClose: () => void;
}

export default function ProjectsOverlay({ open, onClose }: ProjectsOverlayProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [visible, setVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const rafRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const handleClose = useCallback(() => {
    setVisible(false);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(onClose, 400);
  }, [onClose]);

  useEffect(() => {
    if (open) {
      const controller = new AbortController();
      setLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      fetch(`${apiUrl}/api/projects/`, { signal: controller.signal })
        .then((res) => {
          if (!res.ok) throw new Error(res.statusText);
          return res.json();
        })
        .then(setProjects)
        .catch((err) => {
          if (err.name !== 'AbortError') setProjects([]);
        })
        .finally(() => setLoading(false));
      rafRef.current = requestAnimationFrame(() => setVisible(true));
      document.body.style.overflow = 'hidden';
      return () => {
        controller.abort();
        cancelAnimationFrame(rafRef.current);
        clearTimeout(timeoutRef.current);
        document.body.style.overflow = '';
      };
    } else {
      setVisible(false);
      setSelectedProject(null);
      setDetailVisible(false);
      document.body.style.overflow = '';
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') handleClose();
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [open, handleClose]);

  function handleSelectProject(project: Project) {
    setSelectedProject(project);
    requestAnimationFrame(() => setDetailVisible(true));
  }

  function handleBackToList() {
    setDetailVisible(false);
    setTimeout(() => setSelectedProject(null), 400);
  }

  function handleBackdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) handleClose();
  }

  if (!open) return null;

  const allTags = Array.from(new Set(projects.flatMap((p) => p.tags))).sort();
  const filteredProjects = selectedTag
    ? projects.filter((p) => p.tags.includes(selectedTag))
    : projects;

  const videoId = selectedProject ? extractYouTubeId(selectedProject.youtube_url) : null;

  return (
    <div
      className={`projects-overlay ${visible ? 'projects-overlay--visible' : ''}`}
      role="dialog"
      aria-modal="true"
      aria-labelledby="projects-title"
      onClick={handleBackdropClick}
    >
      <button className="projects-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>

      {!selectedProject ? (
        <div className="projects-list">
          <h2 id="projects-title" className="projects-list__title">Nos Projets</h2>
          {loading ? (
            <p className="projects-list__message">Chargement…</p>
          ) : projects.length === 0 ? (
            <p className="projects-list__message">Aucun projet pour le moment.</p>
          ) : (
            <>
            {allTags.length > 0 && (
              <div className="projects-filters">
                <button
                  className={`projects-filters__btn ${selectedTag === null ? 'projects-filters__btn--active' : ''}`}
                  onClick={() => setSelectedTag(null)}
                >
                  Tous
                </button>
                {allTags.map((tag) => (
                  <button
                    key={tag}
                    className={`projects-filters__btn ${selectedTag === tag ? 'projects-filters__btn--active' : ''}`}
                    onClick={() => setSelectedTag(tag)}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            )}
            <div className="projects-grid">
              {filteredProjects.map((project) => (
                <button
                  key={project.id}
                  className={`project-card ${!project.thumbnail_url ? 'project-card--no-thumbnail' : ''}`}
                  onClick={() => handleSelectProject(project)}
                >
                  {project.thumbnail_url && (
                    <>
                      <img
                        src={project.thumbnail_url}
                        alt=""
                        className="project-card__thumbnail"
                      />
                      <div className="project-card__overlay" />
                    </>
                  )}
                  <span className="project-card__tag">
                    {project.tags[0] || ''}
                  </span>
                  <span className="project-card__title">{project.title}</span>
                </button>
              ))}
            </div>
            </>
          )}
        </div>
      ) : (
        <div className={`project-detail ${detailVisible ? 'project-detail--visible' : ''}`}>
          <button className="project-detail__back" onClick={handleBackToList}>
            ← Retour aux projets
          </button>
          <div className="project-detail__content">
            <div className="project-detail__info">
              <h2 className="project-detail__title">{selectedProject.title}</h2>
              <div className="project-detail__tags">
                {selectedProject.tags.map((tag, index) => (
                  <span key={`${tag}-${index}`} className="project-detail__tag">{tag}</span>
                ))}
              </div>
              <p className="project-detail__description">{selectedProject.description}</p>
            </div>
            <div className="project-detail__video">
              {videoId && (
                <iframe
                  src={`https://www.youtube.com/embed/${videoId}`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                  sandbox="allow-scripts allow-same-origin allow-presentation allow-popups"
                  loading="lazy"
                  allowFullScreen
                  title={selectedProject.title}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
