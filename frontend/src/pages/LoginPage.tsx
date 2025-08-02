// frontend/src/pages/LoginPage.tsx

import { supabase } from '../supabaseClient';
import { Auth } from '@supabase/auth-ui-react';
import { ThemeSupa } from '@supabase/auth-ui-shared';
import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

function LoginPage() {
  const navigate = useNavigate();

  // This effect will run when the component mounts and whenever the auth state changes
  useEffect(() => {
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        // If the user is signed in, redirect them to the homepage
        if (session) {
          navigate('/');
        }
      }
    );

    // Cleanup the listener when the component unmounts
    return () => {
      authListener.subscription.unsubscribe();
    };
  }, [navigate]);

  return (
    <main className="relative z-10 max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="pulse-card"> {/* Reusing the card style from App.css */}
        <Auth
          supabaseClient={supabase}
          appearance={{ theme: ThemeSupa }}
          theme="dark"
          providers={['google']} // Optional: Add social logins
        />
      </div>
    </main>
  );
}

export default LoginPage;