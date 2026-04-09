import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Contact — Cultur'all",
};

export default function Contact() {
  return (
    <main className="page">
      <h1>Contact</h1>
      <p>
        Pour toute question ou proposition, n&apos;hésitez pas à nous contacter.
      </p>
    </main>
  );
}
