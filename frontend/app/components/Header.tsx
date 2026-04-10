'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import ProjectsOverlay from './ProjectsOverlay';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function Header() {
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    setMenuOpen(false);
    fetch(`${API_URL}/api/auth/check/`, { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => setAuthenticated(data.authenticated))
      .catch(() => setAuthenticated(false));
  }, [pathname]);

  useEffect(() => {
    if (!menuOpen) return;
    document.body.style.overflow = 'hidden';
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false);
    };
    document.addEventListener('keydown', handleKey);
    return () => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleKey);
    };
  }, [menuOpen]);

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
        <button
          className="header-burger"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
          aria-expanded={menuOpen}
        >
          <span aria-hidden="true">{menuOpen ? '✕' : '☰'}</span>
        </button>
        <nav className={`header-nav${menuOpen ? ' header-nav--open' : ''}`}>
          <button
            className="header-nav__link"
            onClick={() => {
              setMenuOpen(false);
              setProjectsOpen(true);
            }}
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
