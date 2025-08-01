import React from 'react';
import { X, Eye, ExternalLink, Calendar, Globe } from 'lucide-react';
import { Category } from '../types';

interface ArticleModalProps {
  category: Category | null;
  onClose: () => void;
}

export const ArticleModal: React.FC<ArticleModalProps> = ({ category, onClose }) => {
  if (!category) return null;

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
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl border border-gray-700 max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${category.gradient} flex items-center justify-center`}>
              <Globe className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{category.name}</h2>
              <p className="text-gray-400 text-sm">{category.articles.length} articles</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 transition-colors"
          >
            <X className="h-6 w-6 text-gray-300" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-white mb-3">Category Summary</h3>
            <div className="bg-gray-800/50 rounded-lg p-4">
              <p className="text-gray-300 leading-relaxed">{category.summary}</p>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Recent Articles</h3>
            {category.articles.map((article) => (
              <div
                key={article.id}
                className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50 hover:border-cyan-500/50 transition-colors"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-white font-medium text-lg leading-tight pr-4">
                    {article.title}
                  </h4>
                  <div className="flex items-center space-x-2 text-gray-400 text-sm whitespace-nowrap">
                    <Eye className="h-4 w-4" />
                    <span>{article.views.toLocaleString()}</span>
                  </div>
                </div>

                <p className="text-gray-300 text-sm mb-3 leading-relaxed">
                  {article.excerpt}
                </p>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <div className="flex items-center space-x-1">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(article.publishedAt)}</span>
                    </div>
                    <span className="px-2 py-1 bg-gray-700 rounded text-xs">
                      {article.source}
                    </span>
                  </div>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center space-x-1 text-cyan-400 hover:text-cyan-300 transition-colors text-sm"
                  >
                    <span>Read Original</span>
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};