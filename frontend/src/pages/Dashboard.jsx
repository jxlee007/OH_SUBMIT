import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardSummary, getCurrentUser } from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { 
  Users, 
  IndianRupee, 
  Clock, 
  AlertTriangle, 
  Receipt, 
  CheckCircle, 
  RefreshCw,
  PlusCircle,
  ArrowUpRight
} from 'lucide-react';

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const user = getCurrentUser();

  const loadSummary = async () => {
    setLoading(true);
    setError('');
    const res = await getDashboardSummary();
    setLoading(false);
    if (res.success && res.data) {
      setSummary(res.data);
    } else {
      setError(res.error || 'Failed to retrieve live reporting summary.');
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            Subscription Operations
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Real-time PostgreSQL recurring billing metrics and lifecycle monitoring
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={loadSummary}
            disabled={loading}
            className="flex items-center justify-center gap-2 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 shadow-xs transition w-full sm:w-auto"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-indigo-600 dark:text-indigo-400' : 'text-slate-500 dark:text-slate-400'}`} />
            <span>Refresh Live Data</span>
          </button>
          {user?.role === 'admin' && (
            <Link
              to="/subscriptions"
              className="flex items-center justify-center gap-2 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition w-full sm:w-auto"
            >
              <PlusCircle className="w-4 h-4" />
              <span>New Subscription</span>
            </Link>
          )}
        </div>
      </div>

      <AlertBanner type="error" message={error} onClose={() => setError('')} />

      {/* KPI Cards Grid: 1 col below sm (<375px), 2 cols at sm (>=375px), 4 cols at lg (>=1280px) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {/* Active Subscriptions */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-colors">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Subscriptions</span>
            <div className="w-9 h-9 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-slate-900 dark:text-white truncate">
              {loading ? '...' : summary?.active_subscriptions ?? 0}
            </div>
            <div className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1 flex items-center gap-1">
              <span>● Live database count</span>
            </div>
          </div>
        </div>

        {/* Total Revenue */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-colors">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Collected Revenue</span>
            <div className="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
              <IndianRupee className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white truncate">
              {loading ? '...' : `₹${Number(summary?.total_revenue || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">
              Settled payments in PostgreSQL
            </div>
          </div>
        </div>

        {/* Outstanding Receivables */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-colors">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Outstanding Amount</span>
            <div className="w-9 h-9 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white truncate">
              {loading ? '...' : `₹${Number(summary?.outstanding_amount || 0).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}
            </div>
            <div className="text-xs text-amber-700 dark:text-amber-400 font-medium mt-1">
              Confirmed awaiting payment
            </div>
          </div>
        </div>

        {/* Overdue Invoices */}
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between transition-colors">
          <div className="flex items-center justify-between text-slate-500 dark:text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Overdue Invoices</span>
            <div className="w-9 h-9 rounded-xl bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4">
            <div className="text-3xl font-extrabold text-rose-600 dark:text-rose-400 truncate">
              {loading ? '...' : summary?.overdue_invoices ?? 0}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium mt-1">
              Past due date requiring action
            </div>
          </div>
        </div>
      </div>

      {/* Operational Breakdown & Quick Navigation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Invoice Pipeline Status */}
        <div className="bg-white dark:bg-slate-900 p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4 transition-colors">
          <h2 className="text-base font-bold text-slate-900 dark:text-white">Invoice Billing Pipeline</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-700">
              <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase">Draft Invoices</span>
              <span className="text-sm font-bold text-slate-800 dark:text-slate-100">{summary?.draft_invoices ?? 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-amber-50/70 dark:bg-amber-950/30 border border-amber-100 dark:border-amber-900/50">
              <span className="text-xs font-semibold text-amber-800 dark:text-amber-300 uppercase">Confirmed (Pending)</span>
              <span className="text-sm font-bold text-amber-900 dark:text-amber-200">{summary?.confirmed_invoices ?? 0}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-xl bg-emerald-50/70 dark:bg-emerald-950/30 border border-emerald-100 dark:border-emerald-900/50">
              <span className="text-xs font-semibold text-emerald-800 dark:text-emerald-300 uppercase">Paid & Reconciled</span>
              <span className="text-sm font-bold text-emerald-900 dark:text-emerald-200">{summary?.paid_invoices ?? 0}</span>
            </div>
          </div>
        </div>

        {/* 3-Click Navigation Shortcuts */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 p-5 sm:p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-4 transition-colors">
          <h2 className="text-base font-bold text-slate-900 dark:text-white">Core Workflow Actions (3-Click Navigation)</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link
              to="/products"
              className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group min-h-[44px]"
            >
              <div className="w-9 h-9 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 group-hover:bg-indigo-600 text-indigo-600 dark:text-indigo-400 group-hover:text-white flex items-center justify-center shrink-0 transition">
                <ArrowUpRight className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-bold text-slate-900 dark:text-white truncate">Manage Catalog & Plans</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">Define products, billing periods, and pricing</div>
              </div>
            </Link>

            <Link
              to="/subscriptions"
              className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group min-h-[44px]"
            >
              <div className="w-9 h-9 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 group-hover:bg-indigo-600 text-indigo-600 dark:text-indigo-400 group-hover:text-white flex items-center justify-center shrink-0 transition">
                <ArrowUpRight className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-bold text-slate-900 dark:text-white truncate">Subscription Lifecycle</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">Transition Draft → Confirmed → Active → Closed</div>
              </div>
            </Link>

            <Link
              to="/invoices"
              className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group min-h-[44px]"
            >
              <div className="w-9 h-9 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 group-hover:bg-indigo-600 text-indigo-600 dark:text-indigo-400 group-hover:text-white flex items-center justify-center shrink-0 transition">
                <ArrowUpRight className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-bold text-slate-900 dark:text-white truncate">Recurring Invoicing & Tax</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">Generate period invoices with double-billing guard</div>
              </div>
            </Link>

            <Link
              to="/payments"
              className="flex items-start gap-3 p-4 rounded-xl border border-slate-200 dark:border-slate-800 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/30 dark:hover:bg-indigo-950/30 transition group min-h-[44px]"
            >
              <div className="w-9 h-9 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 group-hover:bg-indigo-600 text-indigo-600 dark:text-indigo-400 group-hover:text-white flex items-center justify-center shrink-0 transition">
                <ArrowUpRight className="w-5 h-5" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-bold text-slate-900 dark:text-white truncate">Payment Collection</div>
                <div className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-2">Record payments against confirmed invoices</div>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
