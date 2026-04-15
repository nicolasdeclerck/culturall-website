'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';
const SCROLL_THRESHOLD = 50;

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    let current = window.scrollY > SCROLL_THRESHOLD;
    setScrolled(current);
    const handleScroll = () => {
      const next = window.scrollY > SCROLL_THRESHOLD;
      if (next !== current) {
        current = next;
        setScrolled(next);
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setMenuOpen(false);
    fetch(`${API_URL}/api/auth/check/`, { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => {
        setAuthenticated(data.authenticated);
        setLogoUrl(data.logo_url ?? null);
      })
      .catch(() => {
        setAuthenticated(false);
        setLogoUrl(null);
      });
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
    <header className={`header${scrolled ? ' header--scrolled' : ''}`}>
      <Link href="/" className="header-title">
        {logoUrl ? (
          <Image
            src={logoUrl}
            alt="Cultur'all"
            width={150}
            height={40}
            className="header-logo"
            priority
          />
        ) : (
          "Cultur'all"
        )}
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
        <Link href="/projets" onClick={() => setMenuOpen(false)}>Nos Projets</Link>
        <Link href="/blog" onClick={() => setMenuOpen(false)}>Blog</Link>
        <Link href="/a-propos" onClick={() => setMenuOpen(false)}>À propos</Link>
        <Link href="/contact" onClick={() => setMenuOpen(false)}>Contact</Link>
        {authenticated && (
          <button className="header-nav__link" onClick={handleLogout}>
            Déconnexion
          </button>
        )}
      </nav>
    </header>
  );
}
