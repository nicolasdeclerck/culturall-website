import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "À propos — Cultur'all",
};

export default function APropos() {
  return (
    <main className="page">
      <h1>À propos</h1>
      <p>
        Cultur&apos;all est un projet dédié à la promotion de la culture sous
        toutes ses formes.
      </p>
    </main>
  );
}
