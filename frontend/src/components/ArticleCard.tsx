// frontend/src/components/ArticleCard.tsx

import React from 'react';
import { Eye, Calendar, ExternalLink } from 'lucide-react';
import { Article } from '../types';

interface ArticleCardProps {
  article: Article;
}

export const ArticleCard: React.FC<ArticleCardProps> = ({ article }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-cyan-500/50 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <h4 className="text-white font-medium text-lg leading-tight pr-4">{article.title}</h4>
        <div className="flex items-center space-x-2 text-gray-400 text-sm whitespace-nowrap">
          <Eye className="lucide lucide-eye h-4 w-4" />
          <span>{article.views.toLocaleString()}</span>
        </div>
      </div>
      <p className="text-gray-300 text-sm mb-3 leading-relaxed">{article.excerpt || `An AI-generated summary for the article: ${article.title}`}</p>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-400">
          <div className="flex items-center space-x-1">
            <Calendar className="lucide lucide-calendar h-4 w-4" />
            <span>{formatDate(article.publishedAt)}</span>
          </div>
          <span className="px-2 py-1 bg-gray-700 rounded text-xs">{article.source}</span>
        </div>
        <a href={article.url} target="_blank" rel="noopener noreferrer" className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 transition-colors text-sm">
          <span>Read Original</span>
          <ExternalLink className="lucide lucide-external-link h-4 w-4" />
        </a>
      </div>
    </div>
  );
};