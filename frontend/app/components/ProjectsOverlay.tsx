'use client';

import { useEffect, useState } from 'react';

interface Project {
  id: number;
  title: string;
  description: string;
  youtube_url: string;
  tags: string[];
}

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|embed\/))([a-zA-Z0-9_-]{11})/,
  );
  return match ? match[1] : null;
}

interface ProjectsOverlayProps {
  open: boolean;
  onClose: () => void;
}

export default function ProjectsOverlay({ open, onClose }: ProjectsOverlayProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [visible, setVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);

  useEffect(() => {
    if (open) {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '';
      fetch(`${apiUrl}/api/projects/`)
        .then((res) => res.json())
        .then(setProjects)
        .catch(() => setProjects([]));
      // Trigger enter animation
      requestAnimationFrame(() => setVisible(true));
    } else {
      setVisible(false);
      setSelectedProject(null);
      setDetailVisible(false);
    }
  }, [open]);

  function handleSelectProject(project: Project) {
    setSelectedProject(project);
    requestAnimationFrame(() => setDetailVisible(true));
  }

  function handleBackToList() {
    setDetailVisible(false);
    setTimeout(() => setSelectedProject(null), 400);
  }

  function handleClose() {
    setVisible(false);
    setTimeout(onClose, 400);
  }

  if (!open) return null;

  const videoId = selectedProject ? extractYouTubeId(selectedProject.youtube_url) : null;

  return (
    <div className={`projects-overlay ${visible ? 'projects-overlay--visible' : ''}`}>
      <button className="projects-overlay__close" onClick={handleClose} aria-label="Fermer">
        ✕
      </button>

      {!selectedProject ? (
        <div className="projects-list">
          <h2 className="projects-list__title">Nos Projets</h2>
          <div className="projects-grid">
            {projects.map((project) => (
              <button
                key={project.id}
                className="project-card"
                onClick={() => handleSelectProject(project)}
              >
                <span className="project-card__tag">
                  {project.tags[0] || ''}
                </span>
                <span className="project-card__title">{project.title}</span>
              </button>
            ))}
          </div>
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
                {selectedProject.tags.map((tag) => (
                  <span key={tag} className="project-detail__tag">{tag}</span>
                ))}
              </div>
              <p className="project-detail__description">{selectedProject.description}</p>
            </div>
            <div className="project-detail__video">
              {videoId && (
                <iframe
                  src={`https://www.youtube.com/embed/${videoId}`}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
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
