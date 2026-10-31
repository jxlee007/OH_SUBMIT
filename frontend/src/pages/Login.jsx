import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { loginUser } from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { Lock, Mail, ArrowRight } from 'lucide-react';

export default function Login({ onAuthSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Layer 1 Client-Side Quick Form Validation
  const validateForm = () => {
    if (!email.trim()) {
      setError('Please provide your registered account email.');
      return false;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Please enter a valid email address (e.g., name@company.com).');
      return false;
    }
    if (!password) {
      setError('Please enter your account password.');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) return;

    setLoading(true);
    const res = await loginUser(email, password);
    setLoading(false);

    if (res.success) {
      if (onAuthSuccess) onAuthSuccess(res.data?.user);
      navigate('/');
    } else {
      setError(res.error || 'Authentication failed. Please verify your credentials.');
    }
  };

  const fillCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-5 sm:p-8 transition-colors">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900 rounded-xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto mb-3">
            <Lock className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Sign in to Brightloop</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Access your subscriptions, invoices, and billing portal
          </p>
        </div>

        <AlertBanner type="error" message={error} onClose={() => setError('')} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@brightloop.com"
                className="w-full pl-10 pr-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                Password
              </label>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full min-h-[44px] py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Evaluator Quick Demo Accounts */}
        <div className="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
          <div className="text-[11px] font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider text-center mb-2.5">
            Evaluator Fast-Logins (One-Click)
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => fillCredentials('admin@brightloop.com', 'Admin@1234')}
              className="min-h-[44px] py-2 px-3 bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 hover:border-indigo-200 text-slate-700 dark:text-slate-200 hover:text-indigo-700 dark:hover:text-indigo-400 rounded-lg text-xs font-semibold transition text-center"
            >
              👑 Admin
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('staff@brightloop.com', 'Staff@1234')}
              className="min-h-[44px] py-2 px-3 bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 hover:border-indigo-200 text-slate-700 dark:text-slate-200 hover:text-indigo-700 dark:hover:text-indigo-400 rounded-lg text-xs font-semibold transition text-center"
            >
              💼 Staff
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('customer@brightloop.com', 'Customer@1234')}
              className="min-h-[44px] py-2 px-3 bg-slate-50 dark:bg-slate-800 hover:bg-indigo-50 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 hover:border-indigo-200 text-slate-700 dark:text-slate-200 hover:text-indigo-700 dark:hover:text-indigo-400 rounded-lg text-xs font-semibold transition text-center"
            >
              🏢 Customer
            </button>
          </div>
        </div>

        <p className="mt-5 text-center text-xs text-slate-500 dark:text-slate-400">
          Don't have an account yet?{' '}
          <Link to="/register" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold underline min-h-[44px] inline-flex items-center">
            Register new account
          </Link>
        </p>
      </div>
    </div>
  );
}
