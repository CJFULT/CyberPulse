// frontend/src/pages/PulseDetailPage.tsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../supabaseClient';
import { Pulse } from '../types';
import { PulseDetail } from '../components/PulseDetail';

function PulseDetailPage() {
  const { slug } = useParams<{ slug: string }>(); // Get the pulse ID from the URL
  const navigate = useNavigate();
  const [pulse, setPulse] = useState<Pulse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getPulse = async () => {
      if (!slug) return;
      setLoading(true);

      // Fetch the single pulse that matches the ID from the URL
      const { data, error } = await supabase
        .from('pulses')
        .select(`*, categories ( name, color, gradient )`)
        .eq('slug', slug)
        .single(); // .single() expects only one result

      if (error) {
        console.error("Error fetching pulse:", error);
        navigate('/pulses'); // Redirect to feed if pulse not found
      } else if (data) {
        // Format the data to match the Pulse type
        const formattedPulse = {
          id: data.id,
          slug: data.slug,
          title: data.title,
          blurb: data.blurb,
          content: data.content,
          views: data.view_count,
          createdAt: data.published_date,
          category: data.categories?.name || 'General',
          categoryColor: data.categories?.color || '#ffffff',
          categoryGradient: data.categories?.gradient || 'from-gray-500 to-gray-600',
        };
        setPulse(formattedPulse as unknown as Pulse);
      }
      setLoading(false);
    };

    getPulse();
  }, [slug, navigate]);

  if (loading) {
    return <p className="text-center text-gray-400 py-12">Loading Pulse...</p>;
  }
  
  if (!pulse) {
    return <p className="text-center text-gray-400 py-12">Pulse not found.</p>;
  }

  return <PulseDetail pulse={pulse} onBack={() => navigate('/pulses')} />;
}

export default PulseDetailPage;








// frontend/src/pages/PulseDetailPage.tsx

// function PulseDetailPage() {
//     return (
//       <div className="text-center py-20">
//         <h1 className="text-white text-5xl font-bold">
//           Test
//         </h1>
//         <p className="text-gray-400 mt-4">
//           If you can see this, the page is rendering correctly.
//         </p>
//       </div>
//     );
//   }
  
//   export default PulseDetailPage;