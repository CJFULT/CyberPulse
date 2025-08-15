import React from 'react';
import { Clock, Eye, ExternalLink } from 'lucide-react';
import { Article } from '../types';

interface FeaturedArticleCardProps {
  article: Article;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export const FeaturedArticleCard: React.FC<FeaturedArticleCardProps> = ({ 
  article, 
  size = 'medium',
  className = ''
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getCategoryGradient = (category: string) => {
    switch (category) {
      case 'artificial-intelligence':
        return 'from-cyan-400 to-blue-500';
      case 'cybersecurity':
        return 'from-orange-400 to-red-500';
      case 'blockchain':
        return 'from-purple-400 to-pink-500';
      default:
        return 'from-gray-400 to-gray-600';
    }
  };

  const sizeClasses = {
    small: 'p-4',
    medium: 'p-5',
    large: 'p-6'
  };

  const titleClasses = {
    small: 'text-lg',
    medium: 'text-xl',
    large: 'text-2xl'
  };

  return (
    <div className={`group relative overflow-hidden rounded-xl bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 hover:border-green-500/50 transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-2xl hover:shadow-green-500/20 ${sizeClasses[size]} ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      <div className="relative">
        <div className="flex items-start justify-between mb-3">
          <h3 className={`font-bold text-white group-hover:text-green-400 transition-colors leading-tight pr-3 ${titleClasses[size]}`}>
            {article.title}
          </h3>
          <div className="flex items-center space-x-1 text-gray-400 text-sm whitespace-nowrap">
            <Eye className="h-4 w-4" />
            <span>{article.views.toLocaleString()}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2 mb-3">
          <div className={`px-3 py-1 rounded-full text-xs font-medium text-white bg-gradient-to-r ${getCategoryGradient(article.category)}`}>
            {article.category.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
          </div>
          <div className="flex items-center space-x-1 text-gray-400 text-sm">
            <Clock className="h-3 w-3" />
            <span>{formatDate(article.publishedAt)}</span>
          </div>
        </div>

        <p className="text-gray-300 text-sm leading-relaxed mb-4">
          {article.excerpt}
        </p>

        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400 bg-gray-800/50 px-2 py-1 rounded">
            {article.source}
          </span>
          <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-cyan-400 transition-colors" />
        </div>
      </div>
    </div>
  );
};