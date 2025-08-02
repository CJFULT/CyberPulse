// frontend/src/App.tsx
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthManager';
import { supabase } from './supabaseClient';
import { ParticleBackground } from './components/ParticleBackground';
import { PulseAnimation } from './components/PulseAnimation';
import HomePage from './pages/HomePage'; // Import the renamed HomePage
import PulseFeedPage from './pages/PulseFeedPage'; 
import LoginPage from './pages/LoginPage';

function App() {
  const { session } = useAuth(); // <-- Get the current session
  const navigate = useNavigate();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/'); // Redirect to homepage after logout
  };

  return (
    <div className="min-h-screen text-white overflow-x-hidden">
      <ParticleBackground />
      <PulseAnimation />

      {/* Simple Navigation for now */}
      <nav className="relative z-20 flex justify-center space-x-6 p-4 bg-black bg-opacity-20">
        <Link to="/" className="text-lg hover:text-cyan-400 transition-colors">Categories</Link>
        <Link to="/pulses" className="text-lg hover:text-cyan-400 transition-colors">Pulses</Link>

        {session ? (
          <div className="flex items-center space-x-4">
            <span className="text-gray-300">{session.user.email}</span>
            <button 
              onClick={handleLogout} 
              className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
              Logout
            </button>
          </div>
        ) : (
          <Link to="/login" className="text-lg hover:text-cyan-400 transition-colors">Login</Link>
        )}

      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/pulses" element={<PulseFeedPage />} />
        <Route path="/login" element={<LoginPage />} />
      </Routes>

       <footer className="relative z-10 border-t border-gray-800 mt-16">
          {/* Your original footer can stay here */}
       </footer>
    </div>
  );
}

export default App;