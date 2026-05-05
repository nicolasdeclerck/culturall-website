'use client';

import { useEffect, useState } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

interface SiteSettings {
  background_video_url: string | null;
  background_video_poster_url: string | null;
}

export default function HeroVideo() {
  const [settings, setSettings] = useState<SiteSettings | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/site/settings/`, { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data: SiteSettings | null) => setSettings(data))
      .catch(() => {});
  }, []);

  if (!settings?.background_video_url) {
    return null;
  }

  return (
    <video
      autoPlay
      muted
      loop
      playsInline
      poster={settings.background_video_poster_url ?? undefined}
      src={settings.background_video_url}
    />
  );
}
