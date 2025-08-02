// frontend/src/AuthManager.tsx

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import { supabase } from './supabaseClient';
import { Session } from '@supabase/supabase-js';

// Create a context for the authentication state
const AuthContext = createContext<{ session: Session | null }>({ session: null });

// Create a provider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch the initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    // Listen for changes in authentication state (login, logout)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
      }
    );

    // Cleanup the subscription when the component unmounts
    return () => subscription.unsubscribe();
  }, []);

  // Show a loading indicator while the session is being fetched
  if (loading) {
    return <div className="min-h-screen text-white text-center p-8">Loading session...</div>;
  }

  // Provide the session to all child components
  return (
    <AuthContext.Provider value={{ session }}>
      {children}
    </AuthContext.Provider>
  );
}

// Create a custom hook to easily access the session
export function useAuth() {
  return useContext(AuthContext);
}