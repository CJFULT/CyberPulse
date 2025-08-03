export interface Article {
  id: string;
  slug: string;
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

export interface Pulse {
  id: string;
  slug: string;
  title: string;
  category: string;
  categoryColor: string;
  categoryGradient: string;
  createdAt: string;
  blurb: string;
  content: string;
  views: number;
}