'use client';

import { useMemo, useState, useEffect } from 'react';
import ProjectOverlay, { Project } from '../components/ProjectOverlay';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ProjetsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTag, setSelectedTag] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

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

  const allTags = useMemo(
    () => Array.from(new Set(projects.flatMap((p) => p.tags))).sort(),
    [projects],
  );
  const filtered = useMemo(
    () => selectedTag ? projects.filter((p) => p.tags.includes(selectedTag)) : projects,
    [projects, selectedTag],
  );

  return (
    <div className="page projets-page">
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
              onClick={() => setSelectedProject(project)}
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

      <ProjectOverlay project={selectedProject} onClose={() => setSelectedProject(null)} />
    </div>
  );
}
