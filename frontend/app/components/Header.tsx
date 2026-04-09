'use client';

import Link from 'next/link';
import { useState } from 'react';
import ProjectsOverlay from './ProjectsOverlay';

export default function Header() {
  const [projectsOpen, setProjectsOpen] = useState(false);

  return (
    <>
      <header className="header">
        <Link href="/" className="header-title">
          Cultur&apos;all
        </Link>
        <nav className="header-nav">
          <button
            className="header-nav__link"
            onClick={() => setProjectsOpen(true)}
          >
            Nos Projets
          </button>
          <Link href="/a-propos">À propos</Link>
          <Link href="/contact">Contact</Link>
        </nav>
      </header>
      <ProjectsOverlay open={projectsOpen} onClose={() => setProjectsOpen(false)} />
    </>
  );
}
