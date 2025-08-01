export interface Article {
  id: string;
  title: string;
  content: string;
  url: string;
  publishedAt: string;
  source: string;
  category: string;
  views: number;
  excerpt: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  color: string;
  gradient: string;
  articles: Article[];
  summary: string;
  totalViews: number;
}

export interface RSSFeed {
  id: string;
  url: string;
  name: string;
  active: boolean;
}