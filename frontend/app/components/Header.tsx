'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import ProjectsOverlay from './ProjectsOverlay';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function Header() {
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    fetch(`${API_URL}/api/auth/check/`, { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => setAuthenticated(data.authenticated))
      .catch(() => setAuthenticated(false));
  }, [pathname]);

  async function handleLogout() {
    await fetch(`${API_URL}/api/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
    });
    setAuthenticated(false);
    router.push('/login');
    router.refresh();
  }

  // Don't render the header on the login page
  if (pathname === '/login') return null;

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
          {authenticated && (
            <button className="header-nav__link" onClick={handleLogout}>
              Déconnexion
            </button>
          )}
        </nav>
      </header>
      <ProjectsOverlay open={projectsOpen} onClose={() => setProjectsOpen(false)} />
    </>
  );
}
