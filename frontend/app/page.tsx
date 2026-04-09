'use client';

import { useEffect, useState } from 'react';

export default function Home() {
  const [today, setToday] = useState('');

  useEffect(() => {
    setToday(
      new Date().toLocaleDateString('fr-FR', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    );
  }, []);

  return (
    <main style={{ fontFamily: 'system-ui, sans-serif', padding: '2rem' }}>
      <h1>Hello, World!</h1>
      {today && <p>Nous sommes le <time dateTime={new Date().toISOString().split('T')[0]}>{today}</time>.</p>}
      <p>Bienvenue sur <strong>culturall-website</strong> — Next.js 14 + Django/Wagtail.</p>
      <p>
        Backend : <a href="http://localhost:8000/">localhost:8000</a> ·{' '}
        <a href="http://localhost:8000/admin/">Wagtail admin</a>
      </p>
    </main>
  );
}
