'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const res = await fetch(`${API_URL}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });

      if (res.ok) {
        router.push('/');
        router.refresh();
      } else {
        const body = await res.json();
        setError(body.error || 'Erreur de connexion.');
      }
    } catch {
      setError('Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <div className="login-card">
        <h1 className="login-title">Connexion</h1>
        <p className="login-subtitle">
          Veuillez vous connecter pour accéder au site.
        </p>

        {error && <p className="login-error">{error}</p>}

        <form className="login-form" onSubmit={handleSubmit} noValidate>
          <div className="contact-field">
            <label htmlFor="username">Nom d&apos;utilisateur</label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>

          <div className="contact-field">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="contact-submit login-submit"
            disabled={submitting}
          >
            {submitting ? 'Connexion en cours…' : 'Se connecter'}
          </button>
        </form>
      </div>
    </main>
  );
}
