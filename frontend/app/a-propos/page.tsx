import type { Metadata } from 'next';
import StaticPageContent from '../components/StaticPageContent';

export const metadata: Metadata = {
  title: 'À propos',
};

export const dynamic = 'force-dynamic';

type Props = {
  searchParams: { preview_token?: string };
};

export default function APropos({ searchParams }: Props) {
  return (
    <StaticPageContent
      slug="a-propos"
      fallbackTitle="À propos"
      previewToken={searchParams.preview_token}
    />
  );
}
