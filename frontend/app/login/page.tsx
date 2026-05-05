'use client';

import Image from 'next/image';
import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function LoginPage() {
  const [logoUrl, setLogoUrl] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/auth/check/`, { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => setLogoUrl(data.logo_url ?? null))
      .catch(() => setLogoUrl(null));
  }, []);

  return (
    <main className="under-construction-page">
      {logoUrl ? (
        <Image
          src={logoUrl}
          alt="Cultur'all"
          width={300}
          height={80}
          className="under-construction-logo"
          priority
        />
      ) : (
        <span className="under-construction-fallback">Cultur&apos;all</span>
      )}
      <h1 className="under-construction-title">Site en construction</h1>
    </main>
  );
}
