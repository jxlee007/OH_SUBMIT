import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Register from './pages/Register';
import ProductsPage from './pages/ProductsPage';
import SubscriptionsPage from './pages/SubscriptionsPage';
import InvoicesPage from './pages/InvoicesPage';
import PaymentsPage from './pages/PaymentsPage';
import { restoreSession } from './services/api';

export default function App() {
  const [sessionHydrated, setSessionHydrated] = useState(false);

  useEffect(() => {
    // Silent hydration from httpOnly cookie on page load / browser refresh
    restoreSession().finally(() => {
      setSessionHydrated(true);
    });
  }, []);

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 w-full">
          {sessionHydrated ? (
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/products" element={<ProductsPage />} />
              <Route path="/subscriptions" element={<SubscriptionsPage />} />
              <Route path="/invoices" element={<InvoicesPage />} />
              <Route path="/payments" element={<PaymentsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          ) : (
            <div className="min-h-[50vh] flex items-center justify-center text-sm text-slate-400">
              Connecting session...
            </div>
          )}
        </main>
        <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
          Brightloop Subscription Management System • Odoo x FLUX Hackathon 2026 • Local PostgreSQL
        </footer>
      </div>
    </BrowserRouter>
  );
}
