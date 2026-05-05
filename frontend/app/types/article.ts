export interface Article {
  id: number;
  slug: string;
  title: string;
  summary: string;
  content: string;
  illustration_url: string | null;
  tags: string[];
  created_at: string;
}
