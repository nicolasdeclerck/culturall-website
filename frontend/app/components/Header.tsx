import Link from 'next/link';
import Image from 'next/image';

export default function Header() {
  return (
    <header className="header">
      <Link href="/" className="header-logo" aria-label="Cultur'all - Accueil">
        <Image
          src="/logo.png"
          alt="Cultur'all"
          width={160}
          height={60}
          priority
          className="header-logo-img"
        />
      </Link>
      <nav className="header-nav">
        <Link href="/a-propos">À propos</Link>
        <Link href="/contact">Contact</Link>
      </nav>
    </header>
  );
}
