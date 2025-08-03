// frontend/src/pages/AccountPage.tsx

import { useState, useEffect } from 'react';
import { supabase } from '../supabaseClient';
import { useAuth } from '../AuthManager';

// We can reuse the Pulse type definition
type Pulse = {
  id: number;
  title: string;
  blurb: string;
};

function AccountPage() {
  const { session } = useAuth();
  const [savedPulses, setSavedPulses] = useState<Pulse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getSavedPulses = async () => {
      if (!session?.user) return; // Don't fetch if there's no user

      try {
        setLoading(true);
        // This is a join-like query. It fetches rows from 'saved_pulses'
        // that match the current user, and for each of those rows,
        // it includes all data (*) from the related 'pulses' table.
        const { data, error } = await supabase
          .from('saved_pulses')
          .select(`
            pulses (
              id,
              title,
              blurb
            )
          `)
          .eq('user_id', session.user.id);
        
        if (error) throw error;
        
        if (data) {
          // The data is returned nested, so we need to extract the pulse info
          const pulses = data.map(item => item.pulses).filter(Boolean) as Pulse[];
          setSavedPulses(pulses);
        }

      } catch (error) {
        if (error instanceof Error) {
          console.error("Error fetching saved pulses:", error.message);
        }
      } finally {
        setLoading(false);
      }
    };

    getSavedPulses();
  }, [session]); // Re-run if the session changes

  return (
    <main className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold">Your Account</h1>
        {session && (
          <div className="mt-6 p-4 bg-gray-800 rounded-lg inline-block">
            <p className="text-lg">Logged in as: <span className="font-mono text-cyan-400">{session.user.email}</span></p>
          </div>
        )}
      </div>

      <div>
        <h2 className="text-3xl font-bold mb-6 text-left">Your Saved Pulses</h2>
        {loading ? (
          <p className="text-gray-400">Loading saved pulses...</p>
        ) : savedPulses.length > 0 ? (
          <div className="pulse-list">
            {savedPulses.map(pulse => (
              <div key={pulse.id} className="pulse-card">
                <h3>{pulse.title}</h3>
                <p>{pulse.blurb}</p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">You haven't saved any pulses yet.</p>
        )}
      </div>
    </main>
  );
}

export default AccountPage;