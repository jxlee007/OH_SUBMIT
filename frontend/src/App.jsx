import React, { useState, useEffect } from 'react';
import { Database, ShieldCheck, Cpu, Layout, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { getHealthStatus } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [testEmail, setTestEmail] = useState('');
  const [emailError, setEmailError] = useState('');

  const fetchStatus = async () => {
    setLoading(true);
    const res = await getHealthStatus();
    setHealth(res);
    setLoading(false);
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleEmailValidation = (e) => {
    const val = e.target.value;
    setTestEmail(val);
    
    // Client-side validation with friendly feedback (Odoo rule: Layer 1 validation)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!val) {
      setEmailError('Email is required.');
    } else if (!emailRegex.test(val)) {
      setEmailError('Please enter a valid email address (e.g., user@example.com).');
    } else {
      setEmailError('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800 flex flex-col font-sans">
      {/* Top Navigation Bar - 3-Click Rule & Clean Layout */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-lg bg-[#714B67] flex items-center justify-center text-white font-bold text-lg shadow-sm">
              O
            </div>
            <div>
              <span className="font-bold text-lg text-slate-900 tracking-tight block leading-tight">
                Odoo x FLUX '26
              </span>
              <span className="text-xs text-slate-500 font-medium">Virtual Round Workspace</span>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-50 text-[#714B67] border border-purple-200">
              Team: JAGMOHAN
            </span>
            <button
              onClick={fetchStatus}
              disabled={loading}
              className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-md transition-colors"
              title="Refresh Health Status"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-[#714B67]' : ''}`} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Status Banner */}
        <section className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Architecture & System Health</h1>
              <p className="text-sm text-slate-500 mt-1">
                FastAPI Backend + Local PostgreSQL Database + React / Vite
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              {health?.success ? (
                <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <CheckCircle2 className="w-4 h-4 mr-1.5 text-emerald-600" />
                  PostgreSQL Online & Ready
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
                  <AlertCircle className="w-4 h-4 mr-1.5 text-amber-600" />
                  {health?.message || 'Connecting to Backend...'}
                </span>
              )}
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="flex items-center space-x-3 text-slate-600 mb-2">
                <Database className="w-5 h-5 text-[#714B67]" />
                <span className="text-xs font-semibold uppercase tracking-wider">Database</span>
              </div>
              <p className="text-sm font-bold text-slate-900">PostgreSQL (Local)</p>
              <p className="text-xs text-slate-500 mt-0.5">Relational / Zero BaaS</p>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="flex items-center space-x-3 text-slate-600 mb-2">
                <Cpu className="w-5 h-5 text-[#017E84]" />
                <span className="text-xs font-semibold uppercase tracking-wider">API Layer</span>
              </div>
              <p className="text-sm font-bold text-slate-900">FastAPI + Pydantic v2</p>
              <p className="text-xs text-slate-500 mt-0.5">RESTful Resource Architecture</p>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="flex items-center space-x-3 text-slate-600 mb-2">
                <Layout className="w-5 h-5 text-indigo-600" />
                <span className="text-xs font-semibold uppercase tracking-wider">Frontend</span>
              </div>
              <p className="text-sm font-bold text-slate-900">React + Vite + Tailwind</p>
              <p className="text-xs text-slate-500 mt-0.5">375px / 768px / 1280px Breakpoints</p>
            </div>

            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
              <div className="flex items-center space-x-3 text-slate-600 mb-2">
                <ShieldCheck className="w-5 h-5 text-emerald-600" />
                <span className="text-xs font-semibold uppercase tracking-wider">Validation</span>
              </div>
              <p className="text-sm font-bold text-slate-900">3-Layer Defense</p>
              <p className="text-xs text-slate-500 mt-0.5">Client + Server + DB Constraints</p>
            </div>
          </div>
        </section>

        {/* Interactive Validation Tester (Odoo Layer 1 Demo) */}
        <section className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900">Layer 1 Validation Demo</h2>
          <p className="text-sm text-slate-500 mt-1">
            Tests instant client-side validation with friendly feedback as required by the evaluator briefing.
          </p>

          <div className="mt-4 max-w-md space-y-2">
            <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Test Email Input
            </label>
            <input
              type="text"
              value={testEmail}
              onChange={handleEmailValidation}
              placeholder="e.g., piso@odoo.com"
              className={`w-full px-3.5 py-2.5 rounded-lg border text-sm transition-all outline-none focus:ring-2 ${
                emailError 
                  ? 'border-red-300 focus:ring-red-100 bg-red-50/20 text-red-900' 
                  : testEmail 
                    ? 'border-emerald-300 focus:ring-emerald-100 bg-emerald-50/20' 
                    : 'border-slate-300 focus:ring-purple-100 focus:border-[#714B67]'
              }`}
            />
            {emailError ? (
              <p className="text-xs text-red-600 font-medium flex items-center pt-1">
                <AlertCircle className="w-3.5 h-3.5 mr-1 flex-shrink-0" />
                {emailError}
              </p>
            ) : testEmail ? (
              <p className="text-xs text-emerald-600 font-medium flex items-center pt-1">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1 flex-shrink-0" />
                Valid email format confirmed.
              </p>
            ) : (
              <p className="text-xs text-slate-400 pt-1">Type an invalid or valid email to observe real-time feedback.</p>
            )}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        Odoo x FLUX Lucknow Hackathon 2026 | Solitary Development by Jagmohan Singh Malhi
      </footer>
    </div>
  );
}
