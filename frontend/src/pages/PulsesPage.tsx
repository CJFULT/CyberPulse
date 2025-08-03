// frontend/src/pages/PulsesPage.tsx
import { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { Pulse } from '../types';
import { PulseFeed } from '../components/PulseFeed';
import { PulseDetail } from '../components/PulseDetail';

function PulsesPage() {
  const [pulses, setPulses] = useState<Pulse[]>([]);
  const [selectedPulse, setSelectedPulse] = useState<Pulse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPulses = async () => {
      setLoading(true);
      const { data, error } = await supabase
        .from('pulses')
        .select(`
          *,
          slug,
          categories ( name, color, gradient )
        `)
        .order('published_date', { ascending: false });

      if (error) {
        console.error("Error fetching pulses:", error);
      } else if (data) {
        const formattedPulses = data.map(p => ({
          id: p.id,
          slug: p.slug,
          title: p.title,
          blurb: p.blurb,
          content: p.content,
          views: p.view_count,
          createdAt: p.published_date,
          category: p.categories?.name || 'General',
          categoryColor: p.categories?.color || '#ffffff',
          categoryGradient: p.categories?.gradient || 'from-gray-500 to-gray-600',
        }));
        setPulses(formattedPulses as unknown as Pulse[]);
      }
      setLoading(false);
    };

    getPulses();
  }, []);

  if (loading) {
    return <p className="text-center text-gray-400 py-12">Loading Pulse Feed...</p>;
  }

  // Conditionally render the detail view or the feed view
  if (selectedPulse) {
    return <PulseDetail pulse={selectedPulse} onBack={() => setSelectedPulse(null)} />;
  }

  return <PulseFeed pulses={pulses} onPulseClick={setSelectedPulse} />;
}

export default PulsesPage;