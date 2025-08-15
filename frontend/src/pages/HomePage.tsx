// frontend/src/pages/HomePage.tsx
import { useState, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { Category, Pulse, Article } from '../types';

// Import all necessary components
import { StatsBar } from '../components/StatsBar';
import { CategoryCard } from '../components/CategoryCard';
import { ArticleModal } from '../components/ArticleModal';
import { PulseCard } from '../components/PulseCard';
import { FeaturedArticleCard } from '../components/FeaturedArticleCard';
import { PulseOfTheDay } from '../components/PulseOfTheDay';
import { WeeklyPulse } from '../components/WeeklyPulse';

// Helper function to format data from Supabase to match the component types
const formatPulseData = (p: any): Pulse => ({
  id: p.id,
  slug: p.slug,
  title: p.title,
  blurb: p.blurb,
  content: p.content,
  views: p.view_count || 0,
  createdAt: p.published_date,
  category: p.categories?.name || 'General',
  categoryColor: p.categories?.color || '#ffffff',
  categoryGradient: p.categories?.gradient || 'from-gray-500 to-gray-600',
});

function HomePage() {
  const navigate = useNavigate();
  
  // --- ALL STATE VARIABLES DECLARED CORRECTLY ---
  const [stats, setStats] = useState({ totalArticles: 0, totalViews: 0, totalCategories: 0 });
  const [categories, setCategories] = useState<Category[]>([]);
  const [pulseOfTheDay, setPulseOfTheDay] = useState<Pulse | null>(null);
  const [weeklyPulse, setWeeklyPulse] = useState<Pulse | null>(null);
  const [featuredArticles, setFeaturedArticles] = useState<Article[]>([]);
  const [topCategories, setTopCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);

      const [
        statsData,
        potdData,
        weeklyPulseData,
        featuredArticlesData,
        topCategoriesData
      ] = await Promise.all([
        supabase.rpc('get_dashboard_stats'),
        supabase.from('pulses').select('*, slug, categories ( * )').order('published_date', { ascending: false }).limit(1).single(),
        supabase.from('weekly_pulses').select('*, slug').order('published_date', { ascending: false }).limit(1).single(),
        supabase.from('articles').select('*').order('scraped_date', { ascending: false }).limit(4),
        supabase.from('categories_with_latest_article').select('*').order('latest_article_date', { ascending: false }).limit(3)
      ]);

      if (statsData.data && statsData.data.length > 0) setStats(statsData.data[0]);
      if (potdData.data) setPulseOfTheDay(formatPulseData(potdData.data));
      if (weeklyPulseData.data) {
        setWeeklyPulse({
          ...formatPulseData(weeklyPulseData.data),
          category: 'Weekly Summary',
          categoryGradient: 'from-purple-500 to-pink-500',
        });
      }
      if (featuredArticlesData.data) {
        const formattedArticles = featuredArticlesData.data.map((art: any) => ({
          id: art.id,
          title: art.title,
          url: art.url,
          publishedAt: art.scraped_date,
          views: art.view_count || 0,
          source: new URL(art.url).hostname,
          category: 'Breaking',
          excerpt: (art.raw_content || '').substring(0, 100) + '...',
          content: art.raw_content,
        }));
        setFeaturedArticles(formattedArticles as unknown as Article[]);
      }
      if (topCategoriesData.data) {
        const formattedCategories = topCategoriesData.data.map(cat => ({
            ...cat,
            // You may need to format nested articles if your CategoryCard expects it
            totalViews: (cat.articles || []).reduce((sum, art) => sum + (art.view_count || 0), 0),
            articles: (cat.articles || []).map((art: any) => ({
              id: art.id,
              title: art.title,
              url: art.url,
              publishedAt: art.scraped_date,
              views: art.view_count || 0,
              source: new URL(art.url).hostname,
              category: cat.name,
              excerpt: '',
              content: '',
            })),
        }));
        setTopCategories(formattedCategories as unknown as Category[]);
      }
      
      setLoading(false);
    };

    fetchData().catch(console.error);
  }, []);

  if (loading) {
    return <p className="text-center py-20 text-white">Loading Real-Time Intelligence...</p>;
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-6xl font-bold mb-4">
          <span className="bg-gradient-to-r from-cyan-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Real-Time Tech Intelligence
          </span>
        </h1>
        <p className="text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed">
          AI-powered RSS aggregation that summarizes the latest tech news from across the web
        </p>
      </div>

      {/* <StatsBar {...stats} /> */}

      {weeklyPulse && (
        <div className="mb-16">
           <WeeklyPulse
                pulse={weeklyPulse}
                onClick={() => navigate(`/weekly_pulses/${weeklyPulse.slug}`)}
            />
        </div>
      )}



    {featuredArticles.length >= 4 && weeklyPulse && (
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-orange-400 via-red-500 to-pink-500 bg-clip-text text-transparent">
                Breaking Stories
              </span>
            </h2>
            <p className="text-gray-400 text-lg">The most exciting developments happening right now</p>
          </div>
          
          {/* Restored creative staggered layout for articles */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            <div className="md:col-span-7">
                <PulseOfTheDay 
                    pulse={pulseOfTheDay} 
                    onClick={() => navigate(`/pulses/${pulseOfTheDay.slug}`)} 
                />
            </div>
            <div className="md:col-span-5 space-y-6">
              <FeaturedArticleCard 
                article={featuredArticles[0]} 
                size="medium"
              />
              <FeaturedArticleCard 
                article={featuredArticles[1]} 
                size="medium"
              />
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <div className="md:translate-y-8">
              <FeaturedArticleCard 
                article={featuredArticles[2]} 
                size="medium"
              />
            </div>
            <div className="md:-translate-y-4">
               <FeaturedArticleCard 
                article={featuredArticles[3]} 
                size="large"
                />
            </div>
          </div>
        </div>
      )}


    {topCategories.length > 0 && (
        <div className="mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              <span className="bg-gradient-to-r from-rose-600 via-yellow-500 to-purple-500 bg-clip-text text-transparent">
                Explore Top Categories
              </span>
            </h2>
            <p className="text-gray-400 text-lg">Dive deep into specialized tech domains</p>
          </div>
          
          {/* Restored creative staggered layout for categories */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {topCategories.map((category, index) => (
              <div 
                key={category.id}
                className={`${index === 1 ? 'md:translate-y-8' : ''} ${index === 2 ? 'md:-translate-y-4' : ''}`}
              >
                <CategoryCard
                  key={category.id}
                  category={category}
                  onClick={() => setSelectedCategory(category)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
      {/* --- END OF UPDATE --- */}

      <ArticleModal
        category={selectedCategory}
        onClose={() => setSelectedCategory(null)}
      />

    </div>
  );
}

export default HomePage;