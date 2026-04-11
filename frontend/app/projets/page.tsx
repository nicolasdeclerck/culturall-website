'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ProjetsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/api/projects/`, {
      credentials: 'include',
      signal: controller.signal,
    })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) setProjects(data);
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setProjects([]);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, []);

  const handleSelectProject = useCallback((project: Project) => {
    setSelectedProject(project);
    requestAnimationFrame(() => setDetailVisible(true));
  }, []);

  const handleBackToList = useCallback(() => {
    setDetailVisible(false);
    setTimeout(() => setSelectedProject(null), 400);
  }, []);

  const allTags = useMemo(
    () => Array.from(new Set(projects.flatMap((p) => p.tags))).sort(),
    [projects],
  );
  const filtered = useMemo(
    () => selectedTag ? projects.filter((p) => p.tags.includes(selectedTag)) : projects,
    [projects, selectedTag],
  );

  const videoId = selectedProject ? extractYouTubeId(selectedProject.youtube_url) : null;

  return (
    <div className="page projets-page">
      {!selectedProject ? (
        <>
          <h1>Nos Projets</h1>

          {allTags.length > 0 && (
            <div className="projects-filters">
              <button
                className={`projects-filters__btn${selectedTag === null ? ' projects-filters__btn--active' : ''}`}
                onClick={() => setSelectedTag(null)}
              >
                Tous
              </button>
              {allTags.map((tag) => (
                <button
                  key={tag}
                  className={`projects-filters__btn${selectedTag === tag ? ' projects-filters__btn--active' : ''}`}
                  onClick={() => setSelectedTag(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          )}

          {loading ? (
            <p className="projets-page__message">Chargement…</p>
          ) : filtered.length === 0 ? (
            <p className="projets-page__message">Aucun projet pour le moment.</p>
          ) : (
            <div className="projets-grid">
              {filtered.map((project) => (
                <button
                  key={project.id}
                  className={`project-card${!project.thumbnail_url ? ' project-card--no-thumbnail' : ''}`}
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
          )}
        </>
      ) : (
        <div className={`project-detail${detailVisible ? ' project-detail--visible' : ''}`}>
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
              <div
                className="project-detail__description"
                dangerouslySetInnerHTML={{ __html: selectedProject.description }}
              />
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
