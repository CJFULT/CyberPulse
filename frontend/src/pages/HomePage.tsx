// frontend/src/App.tsx

import React, { useState, useMemo, useEffect } from 'react';
import { supabase } from '../supabaseClient'; // Our Supabase client
import { ParticleBackground } from '../components/ParticleBackground';
import { Header } from '../components/Header';
import { CategoryCard } from '../components/CategoryCard';
import { ArticleModal } from '../components/ArticleModal';
import { StatsBar } from '../components/StatsBar';
import { PulseAnimation } from '../components/PulseAnimation';
import { Category } from '../types'; // Assuming this type is defined correctly

// Define a placeholder for totalViews, as this isn't in our schema yet
const MOCK_TOTAL_VIEWS = 125000; // We can replace this later

function App() {
  // State for holding live data
  const [categories, setCategories] = useState<Category[]>([]);
  const [stats, setStats] = useState({ totalArticles: 0, totalViews: 0, totalCategories: 0 });
  const [loading, setLoading] = useState(true);

  // State for UI interaction (from your original file)
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showMenu, setShowMenu] = useState(false);

  // useEffect to fetch data when the app loads
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      // Fetch categories and their nested articles simultaneously with stats
      const [categoryPromise, statsPromise] = await Promise.all([
        supabase
          .from('categories')
          .select(`
            *,
            articles ( id, title, url )
          `),
        supabase.rpc('get_dashboard_stats') // Calling our new database function
      ]);

      if (categoryPromise.error) console.error('Error fetching categories:', categoryPromise.error);
      if (statsPromise.error) console.error('Error fetching stats:', statsPromise.error);

      if (categoryPromise.data) {
        // The data needs to match the 'Category' type, including 'description' and 'totalViews'
        const formattedCategories = categoryPromise.data.map(cat => ({
          ...cat,
          description: cat.description || `Insights and updates on ${cat.name}.`, // Add placeholder
          totalViews: cat.totalViews || 0, // Add placeholder
          articles: cat.articles || [],
        }));
        setCategories(formattedCategories as unknown as Category[]);
      }

      if (statsPromise.data) {
        const result = statsPromise.data[0];
        setStats({ 
          totalArticles: result.total_articles, 
          totalCategories: result.total_categories,
          totalViews: result.total_views || 0 // Use placeholder for now
        });
      }

      setLoading(false);
    };

    fetchData();
  }, []);

  // Your original search logic, now running on live data!
  const filteredCategories = useMemo(() => {
    if (!searchQuery) return categories;
    return categories.filter(category =>
      category.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (category.description && category.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (category.articles && category.articles.some(article =>
        article.title.toLowerCase().includes(searchQuery.toLowerCase())
      ))
    );
  }, [searchQuery, categories]);

  // The rest of your component remains the same, using the new live data states
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

        <StatsBar {...stats} />

        {loading && <p className="text-center text-gray-400 py-12">Loading intelligence feed...</p>}

        {searchQuery && !loading && (
          <div className="mb-6">
            <p className="text-gray-400">
              Found {filteredCategories.length} categories matching "{searchQuery}"
            </p>
          </div>
        )}

        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredCategories.map((category) => (
              <CategoryCard
                key={category.id}
                category={category}
                onClick={() => setSelectedCategory(category)}
              />
            ))}
          </div>
        )}

        {!loading && filteredCategories.length === 0 && searchQuery && (
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
        {/* Your original footer JSX */}
      </footer>
    </div>
  );
}

export default App;