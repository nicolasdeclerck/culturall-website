'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Project {
  id: number;
  title: string;
  tags: string[];
  thumbnail_url: string | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function ProjectsSection() {
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/api/projects/featured/`, {
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
      });
    return () => controller.abort();
  }, []);

  if (projects.length === 0) return null;

  return (
    <section className="projects-section">
      <h2 className="projects-section__title">Projets</h2>
      <div className="projects-section__cards">
        {projects.map((project) => (
          <Link
            key={project.id}
            href="/projets"
            className={`projects-section__card${!project.thumbnail_url ? ' projects-section__card--no-thumbnail' : ''}`}
          >
            {project.thumbnail_url && (
              <img
                src={project.thumbnail_url}
                alt=""
                className="projects-section__card-image"
              />
            )}
            <div className="projects-section__card-overlay" />
            <span className="projects-section__card-tag">
              {project.tags[0] || ''}
            </span>
            <span className="projects-section__card-title">{project.title}</span>
          </Link>
        ))}
      </div>
      <Link href="/projets" className="projects-section__link">
        Voir tous les projets →
      </Link>
    </section>
  );
}
