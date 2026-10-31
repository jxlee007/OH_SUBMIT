import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { User, Mail, Lock, Check, X, Shield, ArrowRight } from 'lucide-react';

export default function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('customer');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Dynamic Password Policy Checks (Hackathon requirement: 8+ chars, upper, lower, special)
  const checks = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    special: /[^A-Za-z0-9]/.test(password),
  };
  const isPasswordValid = Object.values(checks).every(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Layer 1 Client Validation
    if (!fullName.trim()) {
      setError('Please provide your full legal or business name.');
      return;
    }
    if (!email.trim() || !/\S+@\S+\.\S+/.test(email)) {
      setError('Please provide a valid email address.');
      return;
    }
    if (!isPasswordValid) {
      setError('Password does not meet all required security policy criteria.');
      return;
    }

    setLoading(true);
    const res = await registerUser({
      full_name: fullName,
      email,
      password,
      role,
    });
    setLoading(false);

    if (res.success) {
      setSuccess('Account created successfully! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1200);
    } else {
      setError(res.error || 'Registration failed.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-5 sm:p-8 transition-colors">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900 rounded-xl flex items-center justify-center text-indigo-600 dark:text-indigo-400 mx-auto mb-3">
            <Shield className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Create Account</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Register your Brightloop portal membership
          </p>
        </div>

        <AlertBanner type="error" message={error} onClose={() => setError('')} />
        <AlertBanner type="success" message={success} />

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                Full Name / Company
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Apex Technologies"
                  className="w-full pl-10 pr-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                Account Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full px-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition font-medium"
              >
                <option value="customer">Customer (Portal)</option>
                <option value="staff">Staff (Operational)</option>
                <option value="admin">Admin (Director)</option>
              </select>
            </div>
          </div>

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
                placeholder="billing@apex.com"
                className="w-full pl-10 pr-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 dark:text-slate-500 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a strong password"
                className="w-full pl-10 pr-3.5 py-2.5 min-h-[44px] text-base sm:text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition"
              />
            </div>

            {/* Layer 1 Real-Time Password Policy Feedback */}
            <div className="mt-2.5 p-3.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200/80 dark:border-slate-700 rounded-xl space-y-1.5 text-xs">
              <div className="font-semibold text-slate-600 dark:text-slate-300 mb-1">
                Password Security Requirements:
              </div>
              <div className={`flex items-center gap-1.5 ${checks.length ? 'text-emerald-700 dark:text-emerald-400 font-medium' : 'text-slate-500 dark:text-slate-400'}`}>
                {checks.length ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" /> : <X className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                <span>At least 8 characters</span>
              </div>
              <div className={`flex items-center gap-1.5 ${checks.uppercase ? 'text-emerald-700 dark:text-emerald-400 font-medium' : 'text-slate-500 dark:text-slate-400'}`}>
                {checks.uppercase ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" /> : <X className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                <span>At least one uppercase letter (A-Z)</span>
              </div>
              <div className={`flex items-center gap-1.5 ${checks.lowercase ? 'text-emerald-700 dark:text-emerald-400 font-medium' : 'text-slate-500 dark:text-slate-400'}`}>
                {checks.lowercase ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" /> : <X className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                <span>At least one lowercase letter (a-z)</span>
              </div>
              <div className={`flex items-center gap-1.5 ${checks.special ? 'text-emerald-700 dark:text-emerald-400 font-medium' : 'text-slate-500 dark:text-slate-400'}`}>
                {checks.special ? <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" /> : <X className="w-3.5 h-3.5 text-slate-400 shrink-0" />}
                <span>At least one special symbol (!@#$%^&*)</span>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full min-h-[44px] py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow-sm transition flex items-center justify-center gap-2 disabled:opacity-50 mt-4"
          >
            <span>{loading ? 'Creating Account...' : 'Complete Registration'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <p className="mt-5 text-center text-xs text-slate-500 dark:text-slate-400">
          Already have an account?{' '}
          <Link to="/login" className="text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 font-semibold underline min-h-[44px] inline-flex items-center">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
