'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Project } from '../../types/project';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?.*v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})/,
  );
  return match ? match[1] : null;
}

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

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
        if (Array.isArray(data)) {
          const match = data.find((p: Project) => String(p.id) === params.id) || null;
          setProject(match);
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') setProject(null);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [params.id]);

  if (loading) {
    return (
      <div className="page projets-page">
        <p className="projets-page__message">Chargement…</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="page projets-page">
        <Link href="/projets" className="project-detail__back">← Retour aux projets</Link>
        <h1>Projet introuvable</h1>
        <p>Ce projet n&apos;existe pas ou a été retiré.</p>
      </div>
    );
  }

  const videoId = extractYouTubeId(project.youtube_url);

  return (
    <div className="page projets-page">
      <Link href="/projets" className="project-detail__back">← Retour aux projets</Link>
      <article className="project-detail">
        <h1>{project.title}</h1>
        {project.tags.length > 0 && (
          <div className="content-overlay__tags">
            {project.tags.map((tag, i) => (
              <span key={`${tag}-${i}`} className="content-overlay__tag">{tag}</span>
            ))}
          </div>
        )}
        {(project.year || project.video_duration) && (
          <div className="content-overlay__meta">
            {project.year && <span className="content-overlay__meta-item">Année {project.year}</span>}
            {project.video_duration && <span className="content-overlay__meta-item">Durée {project.video_duration}</span>}
          </div>
        )}
        {project.credits && (
          <div
            className="content-overlay__credits"
            dangerouslySetInnerHTML={{ __html: project.credits }}
          />
        )}
        <div
          className="content-overlay__body"
          dangerouslySetInnerHTML={{ __html: project.description }}
        />
        {videoId && (
          <div className="project-detail__video">
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
      </article>
    </div>
  );
}
