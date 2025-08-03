// frontend/src/pages/PulseFeedPage.tsx

import { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { useAuth } from '../AuthManager';

type Pulse = {
  id: number;
  title: string;
  blurb: string;
  content: string;
  published_date: string;
  is_saved?: boolean; // Add optional property to track saved state
};

function PulseFeedPage() {
  const { session } = useAuth();
  const [pulses, setPulses] = useState<Pulse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPulses = async () => {
      try {
        setLoading(true);
        // Fetch all pulses
        const { data: pulsesData, error: pulsesError } = await supabase
          .from('pulses')
          .select('*')
          .order('published_date', { ascending: false });

        if (pulsesError) throw pulsesError;

        let finalPulses = pulsesData || [];

        // If the user is logged in, fetch their saved pulses
        if (session?.user) {
          const { data: savedPulsesData, error: savedError } = await supabase
            .from('saved_pulses')
            .select('pulse_id')
            .eq('user_id', session.user.id);
          
          if (savedError) throw savedError;

          const savedPulseIds = new Set(savedPulsesData.map(p => p.pulse_id));
          
          // Mark the pulses that are saved by the user
          finalPulses = finalPulses.map(pulse => ({
            ...pulse,
            is_saved: savedPulseIds.has(pulse.id),
          }));
        }
        
        setPulses(finalPulses);

      } catch (error) {
        if (error instanceof Error) {
          console.error("Error fetching pulses:", error.message);
        }
      } finally {
        setLoading(false);
      }
    };
    getPulses();
  }, [session]); // Re-run the effect if the session changes

  const toggleSavePulse = async (pulseId: number, isCurrentlySaved: boolean) => {
    if (!session?.user) {
      alert("Please log in to save pulses.");
      return;
    }

    // Optimistically update the UI
    setPulses(pulses.map(p => p.id === pulseId ? { ...p, is_saved: !isCurrentlySaved } : p));

    if (isCurrentlySaved) {
      // Unsave the pulse
      const { error } = await supabase
        .from('saved_pulses')
        .delete()
        .match({ user_id: session.user.id, pulse_id: pulseId });
      if (error) {
        console.error("Error unsaving pulse:", error);
        // Revert UI on error
        setPulses(pulses.map(p => p.id === pulseId ? { ...p, is_saved: true } : p));
      }
    } else {
      // Save the pulse
      const { error } = await supabase
        .from('saved_pulses')
        .insert({ user_id: session.user.id, pulse_id: pulseId });
      if (error) {
        console.error("Error saving pulse:", error);
        // Revert UI on error
        setPulses(pulses.map(p => p.id === pulseId ? { ...p, is_saved: false } : p));
      }
    }
  };

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* ... header ... */}
      
      {loading ? (
        <p className="text-center text-gray-400">Loading feed...</p>
      ) : (
        <div className="pulse-list">
          {pulses.map((pulse) => (
            <div key={pulse.id} className="pulse-card flex justify-between items-start">
              <div>
                <h2>{pulse.title}</h2>
                <p>{pulse.blurb}</p>
                <small>Published: {new Date(pulse.published_date).toLocaleDateString()}</small>
              </div>
              {session && (
                <button 
                  onClick={() => toggleSavePulse(pulse.id, !!pulse.is_saved)}
                  className={`p-2 rounded-lg transition-colors ${pulse.is_saved ? 'bg-pink-600 hover:bg-pink-700' : 'bg-gray-600 hover:bg-gray-700'}`}
                  aria-label={pulse.is_saved ? 'Unsave Pulse' : 'Save Pulse'}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill={pulse.is_saved ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 015.656 0L12 8.428l2.026-2.11a4.5 4.5 0 115.656 6.364l-7.682 8.04-7.682-8.04a4.5 4.5 0 010-6.364z" />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default PulseFeedPage;