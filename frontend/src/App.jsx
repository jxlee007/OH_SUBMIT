import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import ProductsPage from './pages/ProductsPage';
import SubscriptionsPage from './pages/SubscriptionsPage';
import InvoicesPage from './pages/InvoicesPage';
import PaymentsPage from './pages/PaymentsPage';
import { restoreSession, getCurrentUser } from './services/api';
import notify from './services/notify';
import { useTheme } from './utils/theme';

function ProtectedRoute({ user, children }) {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function PublicOnlyRoute({ user, children }) {
  if (user) {
    return <Navigate to="/" replace />;
  }
  return children;
}

export default function App() {
  const [currentUser, setCurrentUser] = useState(null);
  const [sessionHydrated, setSessionHydrated] = useState(false);
  const { isDark } = useTheme();
  const [isMdUp, setIsMdUp] = useState(
    typeof window !== 'undefined' ? window.innerWidth >= 768 : true
  );

  useEffect(() => {
    const handleResize = () => setIsMdUp(window.innerWidth >= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const handleOffline = () => {
      notify.warning('You are offline. Changes will not be saved.', {
        toastId: 'offline-status',
      });
    };
    const handleOnline = () => {
      notify.info('Back online.', {
        toastId: 'online-status',
      });
    };

    window.addEventListener('offline', handleOffline);
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('online', handleOnline);
    };
  }, []);

  useEffect(() => {
    // Silent hydration from httpOnly cookie on page load / browser refresh
    restoreSession()
      .then((user) => {
        setCurrentUser(user);
      })
      .catch(() => {
        setCurrentUser(null);
      })
      .finally(() => {
        setSessionHydrated(true);
      });
  }, []);

  const handleAuthSuccess = (user) => {
    setCurrentUser(user || getCurrentUser());
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
        <Navbar user={currentUser} onLogout={handleLogout} />
        <ToastContainer
          position={isMdUp ? 'top-right' : 'top-center'}
          theme={isDark ? 'dark' : 'light'}
          newestOnTop
          closeOnClick
          pauseOnHover
        />
        <main className="flex-1 w-full max-w-full overflow-x-hidden">
          {sessionHydrated ? (
            <Routes>
              {/* Public-only routes: logged in users are redirected to / */}
              <Route
                path="/login"
                element={
                  <PublicOnlyRoute user={currentUser}>
                    <Login onAuthSuccess={handleAuthSuccess} />
                  </PublicOnlyRoute>
                }
              />
              <Route
                path="/register"
                element={
                  <PublicOnlyRoute user={currentUser}>
                    <Register />
                  </PublicOnlyRoute>
                }
              />

              {/* Protected routes: unauthenticated visitors bounced to /login */}
              <Route
                path="/"
                element={
                  <ProtectedRoute user={currentUser}>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/products"
                element={
                  <ProtectedRoute user={currentUser}>
                    <ProductsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/subscriptions"
                element={
                  <ProtectedRoute user={currentUser}>
                    <SubscriptionsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/invoices"
                element={
                  <ProtectedRoute user={currentUser}>
                    <InvoicesPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/payments"
                element={
                  <ProtectedRoute user={currentUser}>
                    <PaymentsPage />
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          ) : (
            <div className="min-h-[50vh] flex items-center justify-center text-sm text-slate-400 dark:text-slate-500">
              Connecting session...
            </div>
          )}
        </main>
        <footer className="bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 py-4 px-4 text-center text-xs text-slate-500 dark:text-slate-400 transition-colors">
          Brightloop Subscription Management System • Odoo x FLUX Hackathon 2026 • Local PostgreSQL
        </footer>
      </div>
    </BrowserRouter>
  );
}
