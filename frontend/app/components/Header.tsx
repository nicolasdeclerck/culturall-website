import Link from 'next/link';

export default function Header() {
  return (
    <header className="header">
      <Link href="/" className="header-title">
        Cultur&apos;all
      </Link>
      <nav className="header-nav">
        <Link href="/a-propos">À propos</Link>
        <Link href="/contact">Contact</Link>
      </nav>
    </header>
  );
}
