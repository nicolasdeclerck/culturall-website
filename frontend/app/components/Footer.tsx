import Link from 'next/link';

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="site-footer__content">
        <Link href="/mentions-legales" className="site-footer__link">
          Mentions légales
        </Link>
        <span className="site-footer__copyright">
          © {new Date().getFullYear()} Cultur&apos;all. Tous droits réservés.
        </span>
      </div>
    </footer>
  );
}
