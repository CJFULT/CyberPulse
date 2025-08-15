// frontend/src/pages/HomePage.tsx

import React, { useState, useMemo, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { ParticleBackground } from '../components/ParticleBackground';
import { Header } from '../components/Header';
import { CategoryCard } from '../components/CategoryCard';
import { ArticleModal } from '../components/ArticleModal';
import { StatsBar } from '../components/StatsBar';
import { PulseAnimation } from '../components/PulseAnimation';
import { Category } from '../types';

function HomePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [stats, setStats] = useState({ totalArticles: 0, totalViews: 0, totalCategories: 0 });
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      const [categoryPromise, statsPromise] = await Promise.all([
        supabase
          .from('categories_with_latest_article')
          .select(`*`)
          .order('latest_article_date', { ascending: false }),
        supabase.rpc('get_dashboard_stats')
      ]);

      if (categoryPromise.error) console.error('Error fetching categories:', categoryPromise.error);
      if (statsPromise.error) console.error('Error fetching stats:', statsPromise.error);

      if (categoryPromise.data) {
        // --- CHECKPOINT 1: Log the raw data from Supabase ---
        // console.log("Checkpoint 1: Raw data from Supabase", categoryPromise.data);

        const formattedCategories = categoryPromise.data.map(cat => {
          const articles = (cat.articles || []).map(art => ({
            id: art.id,
            title: art.title,
            url: art.url,
            publishedAt: art.scraped_date,
            views: art.view_count,
            content: '', 
            source: new URL(art.url).hostname,
            category: cat.name,
            excerpt: '',
          }));
          
          // --- CHECKPOINT 2: Log each category as it's being formatted ---
          // console.log(`Checkpoint 2: Formatting category "${cat.name}". Found ${articles.length} articles.`);

          return {
            id: cat.id,
            name: cat.name,
            description: cat.description || cat.name,
            color: cat.color,
            gradient: cat.gradient,
            summary: cat.description,
            totalViews: articles.reduce((sum, art) => sum + (art.views || 0), 0),
            articles: articles,
          };
        });

        // --- CHECKPOINT 3: Log the final data being set to state ---
        // console.log("Checkpoint 3: Final data being set", formattedCategories);
        
        setCategories(formattedCategories as unknown as Category[]);
      }

      if (statsPromise.data) {
        const result = statsPromise.data[0];
        setStats({ 
          totalArticles: result.total_articles || 0, 
          totalCategories: result.total_categories || 0,
          totalViews: result.total_views || 0,
        });
      }

      setLoading(false);
    };

    fetchData();
  }, []);

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

  return (
    <>
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
    </>
  );
}

export default HomePage;