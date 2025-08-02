// frontend/src/pages/PulseFeedPage.tsx

import { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';

type Pulse = {
  id: number;
  title: string;
  blurb: string;
  content: string;
  published_date: string;
};

function PulseFeedPage() {
  const [pulses, setPulses] = useState<Pulse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPulses = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('pulses')
          .select('*')
          .order('published_date', { ascending: false });

        if (error) throw error;
        if (data) setPulses(data);
      } catch (error) {
        if (error instanceof Error) {
          console.error("Error fetching pulses:", error.message);
        }
      } finally {
        setLoading(false);
      }
    };
    getPulses();
  }, []);

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl md:text-5xl font-bold">
          <span className="bg-gradient-to-r from-green-400 via-teal-500 to-blue-500 bg-clip-text text-transparent">
            Latest Intelligence Pulses
          </span>
        </h1>
        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
          AI-generated summaries of the latest trends and events.
        </p>
      </div>
      
      {loading ? (
        <p className="text-center text-gray-400">Loading feed...</p>
      ) : (
        <div className="pulse-list">
          {pulses.map((pulse) => (
            <div key={pulse.id} className="pulse-card">
              <h2>{pulse.title}</h2>
              <p>{pulse.blurb}</p>
              <small>Published: {new Date(pulse.published_date).toLocaleDateString()}</small>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default PulseFeedPage;