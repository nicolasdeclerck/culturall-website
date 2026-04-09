import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'culturall-website',
  description: 'Site vitrine — Next.js + Django/Wagtail',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
