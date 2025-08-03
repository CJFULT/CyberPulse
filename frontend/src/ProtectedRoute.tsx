// frontend/src/ProtectedRoute.tsx

import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthManager';
import { ReactNode } from 'react';

function ProtectedRoute({ children }: { children: ReactNode }) {
  const { session } = useAuth();

  // If there is no active session, redirect the user to the login page
  if (!session) {
    return <Navigate to="/login" replace />;
  }

  // If there is a session, render the child components (the protected page)
  return <>{children}</>;
}

export default ProtectedRoute;