// frontend/src/components/ArticleModal.tsx

import React from 'react';
import { X } from 'lucide-react';
import { Category } from '../types';
import { ArticleCard } from './ArticleCard';
// We'll need to import the icon mapping we will create
import { categoryIcons } from './CategoryCard'; 

interface ArticleModalProps {
  category: Category | null;
  onClose: () => void;
}

export const ArticleModal: React.FC<ArticleModalProps> = ({ category, onClose }) => {
  if (!category) return null;

  // Get the correct icon for the category
  const IconComponent = categoryIcons[category.name] || categoryIcons.Default;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors z-10"
        >
          <X className="h-6 w-6" />
        </button>

        {/* --- MODIFIED HEADER --- */}
        <header className="p-8 border-b border-gray-700 flex items-center space-x-4">
          <div className={`p-3 rounded-lg bg-gradient-to-br ${category.gradient}`}>
            <IconComponent className="h-8 w-8 text-white" />
          </div>
          <div>
            <h2 className={`text-3xl font-bold bg-gradient-to-r ${category.gradient} bg-clip-text`}>
              {category.name}
            </h2>
          </div>
        </header>
        {/* --- END OF MODIFICATION --- */}

        {/* --- MODIFIED LAYOUT --- */}
        <div className="flex-grow overflow-y-auto p-8 space-y-8">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Category Summary</h3>
            <div className="p-4 bg-gray-800/50 rounded-lg">
              <p className="text-gray-300 leading-relaxed">{category.summary}</p>
            </div>
          </div>
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Recent Articles ({category.articles.length})</h3>
            <div className="space-y-4">
              {category.articles.length > 0 ? (
                category.articles.slice(0, 5).map((article) => (
                  <ArticleCard key={article.id} article={article} />
                ))
              ) : (
                <p className="text-gray-500">No articles found for this category yet.</p>
              )}
            </div>
          </div>
        </div>
        {/* --- END OF MODIFICATION --- */}
      </div>
    </div>
  );
};