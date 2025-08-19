// frontend/src/pages/WeeklyPulseDetailPage.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { Pulse } from '../types'; // We can reuse the Pulse type
import { ArrowLeft, Clock, Eye } from 'lucide-react';

function WeeklyPulseDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [pulse, setPulse] = useState<Pulse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPulse = async () => {
      if (!slug) return;
      setLoading(true);

      const { data, error } = await supabase
        .from('weekly_pulses')
        .select(`*`)
        .eq('slug', slug)
        .single();

      if (error) {
        console.error("Error fetching weekly pulse:", error);
        navigate('/'); // Go back to homepage on error
      } else if (data) {
        setPulse({
          id: data.id,
          slug: data.slug,
          title: data.title,
          blurb: data.blurb,
          content: data.content,
          views: data.view_count || 0,
          createdAt: data.published_date,
          category: 'Weekly Summary',
          categoryColor: '',
          categoryGradient: 'from-purple-500 to-pink-500',
        });
      }
      setLoading(false);
    };
    getPulse();
  }, [slug, navigate]);

  const renderContentWithBulletPoints = (content: string) => {
    const parts = content.split('What to Watch For:');
    const mainContent = parts[0];
    const watchForContent = parts[1];

    const bulletPoints = watchForContent?.split('- ').filter(item => item.trim() !== '').map((item, index) => (
      <li key={index} className="mb-2">{item.trim()}</li>
    ));

    return (
      <div>
        <p className="whitespace-pre-line">{mainContent}</p>
        {bulletPoints && (
          <div className="mt-6">
            <h3 className="text-2xl font-bold text-white mb-4">What to Watch For:</h3>
            <ul className="list-disc list-inside text-gray-300">
              {bulletPoints}
            </ul>
          </div>
        )}
      </div>
    );
  };
  
  if (loading) return <p className="text-center text-gray-400 py-12">Loading Weekly Pulse...</p>;
  if (!pulse) return <p className="text-center text-gray-400 py-12">Weekly Pulse not found.</p>;

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-cyan-400 hover:text-cyan-300 transition-colors mb-8 group"
      >
        <ArrowLeft className="h-5 w-5 group-hover:-translate-x-1 transition-transform" />
        <span>Back to Home</span>
      </button>

      <article className="bg-gradient-to-br from-gray-900/90 to-gray-800/90 border border-gray-700/50 rounded-xl p-8">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-4 leading-tight">{pulse.title}</h1>
        </header>

        <div className="text-gray-300 text-lg leading-relaxed">
          {renderContentWithBulletPoints(pulse.content)}
        </div>
      </article>
    </div>
  );
}

export default WeeklyPulseDetailPage;