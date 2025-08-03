// frontend/src/App.tsx
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useAuth } from './AuthManager';
import { supabase } from './supabaseClient';
import { ParticleBackground } from './components/ParticleBackground';
import { PulseAnimation } from './components/PulseAnimation';
import HomePage from './pages/HomePage'; // Import the renamed HomePage
import PulsesPage from './pages/PulsesPage'; 
import PulseDetailPage from './pages/PulseDetailPage';
import LoginPage from './pages/LoginPage';
import AccountPage from './pages/AccountPage';
import ProtectedRoute from './ProtectedRoute';

function App() {
  const { session } = useAuth(); // <-- Get the current session
  const navigate = useNavigate();

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/'); // Redirect to homepage after logout
  };

  return (
    <div className="min-h-screen text-white overflow-x-hidden">
      <div className="fixed inset-0 z-0"> {/* <-- WRAP AND ADD z-0 */}
        <ParticleBackground />
      </div>
      <PulseAnimation />

      {/* Simple Navigation for now */}
      <div className="relative z-10 flex flex-col min-h-screen">
        <nav className="relative z-20 flex justify-center space-x-6 p-4 bg-black bg-opacity-20">
          <Link to="/" className="text-lg hover:text-cyan-400 transition-colors">Categories</Link>
          <Link to="/pulses" className="text-lg hover:text-cyan-400 transition-colors">Pulses</Link>

          {session ? (
            <div className="flex items-center space-x-4">
              <Link to="/account" className="text-lg hover:text-cyan-400 transition-colors">Account</Link>
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
          <Route path="/pulses" element={<PulsesPage />} />
          <Route path="/pulses/:slug" element={<PulseDetailPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/account" element={<ProtectedRoute><AccountPage /></ProtectedRoute>}/>
        </Routes>

        <footer className="relative z-10 border-t border-gray-800 mt-16">
            {/* Your original footer can stay here */}
        </footer>
       </div>
    </div>
  );
}

export default App;