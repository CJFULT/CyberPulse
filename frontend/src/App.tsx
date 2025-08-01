import React, { useState, useMemo } from 'react';
import { ParticleBackground } from './components/ParticleBackground';
import { Header } from './components/Header';
import { CategoryCard } from './components/CategoryCard';
import { ArticleModal } from './components/ArticleModal';
import { StatsBar } from './components/StatsBar';
import { PulseAnimation } from './components/PulseAnimation';
import { mockCategories } from './data/mockData';
import { Category } from './types';

function App() {
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showMenu, setShowMenu] = useState(false);

  const filteredCategories = useMemo(() => {
    if (!searchQuery) return mockCategories;
    return mockCategories.filter(category =>
      category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      category.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      category.articles.some(article =>
        article.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    );
  }, [searchQuery]);

  const totalStats = useMemo(() => {
    const totalArticles = mockCategories.reduce((sum, cat) => sum + cat.articles.length, 0);
    const totalViews = mockCategories.reduce((sum, cat) => sum + cat.totalViews, 0);
    return { totalArticles, totalViews, totalCategories: mockCategories.length };
  }, []);

  return (
    <div className="min-h-screen text-white overflow-x-hidden">
      <ParticleBackground />
      <PulseAnimation />
      
      <Header
        onMenuClick={() => setShowMenu(!showMenu)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-6xl font-bold mb-4">
            <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
              Real-Time Tech Intelligence
            </span>
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
            AI-powered RSS aggregation that categorizes and summarizes the latest tech news from across the web
          </p>
        </div>

        <StatsBar {...totalStats} />

        {searchQuery && (
          <div className="mb-6">
            <p className="text-gray-400">
              Found {filteredCategories.length} categories matching "{searchQuery}"
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredCategories.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              onClick={() => setSelectedCategory(category)}
            />
          ))}
        </div>

        {filteredCategories.length === 0 && searchQuery && (
          <div className="text-center py-12">
            <p className="text-gray-400 text-lg">No categories found matching your search.</p>
          </div>
        )}
      </main>

      <ArticleModal
        category={selectedCategory}
        onClose={() => setSelectedCategory(null)}
      />

      <footer className="relative z-10 border-t border-gray-800 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-cyan-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">CP</span>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-500 bg-clip-text text-transparent">
                CyberPulse
              </span>
            </div>
            <p className="text-gray-400">
              Powered by AI • Real-time RSS Processing • Built for the Future
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;