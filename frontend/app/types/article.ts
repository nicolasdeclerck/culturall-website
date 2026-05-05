export interface Article {
  id: number;
  title: string;
  summary: string;
  content: string;
  illustration_url: string | null;
  tags: string[];
  created_at: string;
}
