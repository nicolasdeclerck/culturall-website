'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useSearchParams } from 'next/navigation';
import { Project } from '../../types/project';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

function extractYouTubeId(url: string): string | null {
  const match = url.match(
    /(?:youtu\.be\/|youtube\.com\/(?:watch\?.*v=|embed\/|shorts\/))([a-zA-Z0-9_-]{11})/,
  );
  return match ? match[1] : null;
}

export default function ProjectDetailPage() {
  const params = useParams<{ slug: string }>();
  const searchParams = useSearchParams();
  const previewToken = searchParams.get('preview_token');

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    if (!params.slug) return;
    const controller = new AbortController();

    const url = previewToken
      ? `${API_URL}/api/preview/project/?token=${encodeURIComponent(previewToken)}`
      : `${API_URL}/api/projects/${encodeURIComponent(params.slug)}/`;

    fetch(url, {
      credentials: 'include',
      signal: controller.signal,
    })
      .then((res) => {
        if (res.status === 404) return null;
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => setProject(data ?? null))
      .catch((err) => {
        if (err.name !== 'AbortError') setProject(null);
      })
      .finally(() => setLoading(false));
    return () => controller.abort();
  }, [params.slug, previewToken]);

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_URL}/api/auth/check/`, {
      credentials: 'include',
      signal: controller.signal,
    })
      .then((res) => res.json())
      .then((data) => setIsAdmin(Boolean(data.is_admin)))
      .catch(() => setIsAdmin(false));
    return () => controller.abort();
  }, []);

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
        <div className="project-detail-wrapper">
          <Link href="/projets" className="project-detail__back">
            <span className="project-detail__back-icon" aria-hidden="true">←</span>
            <span>Projets</span>
          </Link>
          <h1>Projet introuvable</h1>
          <p>Ce projet n&apos;existe pas ou a été retiré.</p>
        </div>
      </div>
    );
  }

  const videoId = extractYouTubeId(project.youtube_url);

  return (
    <div className="page projets-page">
      {previewToken && (
        <div className="preview-banner" role="status">
          <span>Mode aperçu — ce contenu n&apos;est pas encore publié</span>
          <Link href={`/projets/${params.slug}`} className="preview-banner__exit">
            Quitter l&apos;aperçu
          </Link>
        </div>
      )}
      <div className="project-detail-wrapper">
        <div className="project-detail__actions">
          <Link href="/projets" className="project-detail__back">
            <span className="project-detail__back-icon" aria-hidden="true">←</span>
            <span>Projets</span>
          </Link>
          {isAdmin && (
            <a
              href={`/admin/pages/${project.id}/edit/`}
              className="project-detail__edit"
            >
              Modifier
            </a>
          )}
        </div>
        <article className="project-detail">
        <h1>{project.title}</h1>
        {(project.tags.length > 0 || project.year || project.video_duration) && (
          <div className="project-detail__byline">
            {project.tags.map((tag, i) => (
              <span key={`tag-${i}`} className="project-detail__byline-item">{tag}</span>
            ))}
            {project.year && <span className="project-detail__byline-item">{project.year}</span>}
            {project.video_duration && (
              <span className="project-detail__byline-item">{project.video_duration}</span>
            )}
          </div>
        )}
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
        <div className="project-detail__content">
          <div
            className="content-overlay__body"
            dangerouslySetInnerHTML={{ __html: project.description }}
          />
          {project.credits && (
            <aside className="project-detail__credits">
              <h2 className="project-detail__credits-heading">Crédits</h2>
              <div
                className="project-detail__credits-body"
                dangerouslySetInnerHTML={{ __html: project.credits }}
              />
            </aside>
          )}
        </div>
        </article>
      </div>
    </div>
  );
}
