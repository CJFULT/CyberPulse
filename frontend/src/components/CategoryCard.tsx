import React from 'react';
import { Eye, ExternalLink, TrendingUp } from 'lucide-react';
import { Category } from '../types';

interface CategoryCardProps {
  category: Category;
  onClick: () => void;
}

export const CategoryCard: React.FC<CategoryCardProps> = ({ category, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="group relative overflow-hidden rounded-xl bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 hover:border-cyan-500/50 transition-all duration-300 cursor-pointer hover:scale-105 hover:shadow-2xl hover:shadow-cyan-500/20"
    >
      <div className={`absolute inset-0 bg-gradient-to-br ${category.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-300`} />
      
      <div className="relative p-6">
        <div className="flex items-center justify-between mb-4">
          <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${category.gradient} flex items-center justify-center`}>
            <TrendingUp className="h-6 w-6 text-white" />
          </div>
          <div className="flex items-center space-x-2 text-gray-400">
            <Eye className="h-4 w-4" />
            <span className="text-sm">{category.totalViews.toLocaleString()}</span>
          </div>
        </div>

        <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">
          {category.name}
        </h3>
        
        <p className="text-gray-400 text-sm mb-4">
          {category.description}
        </p>

        <div className="bg-gray-800/50 rounded-lg p-3 mb-4">
          <p className="text-gray-300 text-sm leading-relaxed">
            {category.summary}
          </p>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-400">
            {category.articles.length} articles
          </span>
          <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-cyan-400 transition-colors" />
        </div>
      </div>
    </div>
  );
};