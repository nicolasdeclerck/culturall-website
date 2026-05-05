export interface Project {
  id: number;
  title: string;
  description: string;
  youtube_url: string;
  tags: string[];
  thumbnail_url: string | null;
  year: string;
  video_duration: string;
  credits: string;
}
