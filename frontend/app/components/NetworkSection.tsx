'use client';

import { useEffect, useState } from 'react';

interface NetworkMember {
  id: number;
  name: string;
  member_type: string;
  logo_url: string | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function NetworkSection() {
  const [members, setMembers] = useState<NetworkMember[]>([]);
  const [activeType, setActiveType] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/network/`, { credentials: 'include' })
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data) => {
        if (Array.isArray(data)) setMembers(data);
      })
      .catch(() => {});
  }, []);

  const types = Array.from(new Set(members.map((m) => m.member_type))).sort();

  const filtered = activeType
    ? members.filter((m) => m.member_type === activeType)
    : members;

  const handleFilter = (type: string | null) => setActiveType(type);

  if (members.length === 0) return null;

  return (
    <section className="network-section">
      <h2 className="network-section__title">Notre Réseau</h2>

      {types.length > 1 && (
        <div className="network-filters">
          <button
            className={`network-filters__btn${activeType === null ? ' network-filters__btn--active' : ''}`}
            onClick={() => handleFilter(null)}
          >
            Tous
          </button>
          {types.map((type) => (
            <button
              key={type}
              className={`network-filters__btn${activeType === type ? ' network-filters__btn--active' : ''}`}
              onClick={() => handleFilter(type)}
            >
              {type}
            </button>
          ))}
        </div>
      )}

      <div className="network-grid" key={activeType ?? '__all__'}>
        {filtered.map((member, i) => (
          <div key={member.id} className="network-card" title={member.name} style={{ animationDelay: `${i * 0.04}s` }}>
            {member.logo_url ? (
              <img
                src={member.logo_url}
                alt={member.name}
                className="network-card__logo"
              />
            ) : (
              <span className="network-card__name">{member.name}</span>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
