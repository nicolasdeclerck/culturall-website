import type { Metadata, Viewport } from 'next';
import './globals.css';
import Header from './components/Header';
import Footer from './components/Footer';

export const metadata: Metadata = {
  title: { default: "Cultur'all", template: "%s — Cultur'all" },
  description: "Cultur'all — Site vitrine",
};

// Sans cette meta, les navigateurs (y compris Chromium headless utilisé par
// agent-browser / les TNR) utilisent un layout viewport fixe (~980px) même
// quand la fenêtre fait 375px, ce qui empêche les media queries
// `(max-width: 768px)` de se déclencher — le menu hamburger et la grille
// blog mono-colonne restent donc invisibles en TNR.
export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
