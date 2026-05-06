import type { Metadata } from 'next';
import StaticPageContent from '../components/StaticPageContent';

export const metadata: Metadata = {
  title: 'Mentions légales',
};

export const dynamic = 'force-dynamic';

type Props = {
  searchParams: { preview_token?: string };
};

export default function MentionsLegales({ searchParams }: Props) {
  return (
    <StaticPageContent
      slug="mentions-legales"
      fallbackTitle="Mentions légales"
      previewToken={searchParams.preview_token}
    />
  );
}
