import React, { useEffect, useState } from 'react';
import { 
  getInvoices, 
  generateInvoice, 
  updateInvoiceStatus, 
  getSubscriptions, 
  getCurrentUser 
} from '../services/api';
import notify from '../services/notify';
import { Receipt, Plus, AlertCircle, Filter, ChevronDown, ChevronUp } from 'lucide-react';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [activeSubscriptions, setActiveSubscriptions] = useState([]);
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const user = getCurrentUser();

  // Generate Invoice Form
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedSubId, setSelectedSubId] = useState('');
  const [billingPeriodKey, setBillingPeriodKey] = useState('2026-11');
  const [dueDate, setDueDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchData = async () => {
    setLoading(true);
    const [invRes, subRes] = await Promise.all([
      getInvoices(overdueOnly, statusFilter),
      getSubscriptions('active'),
    ]);
    setLoading(false);

    if (invRes.success) setInvoices(invRes.data || []);
    else notify.error(invRes.error || 'Failed to fetch invoices');

    if (subRes.success && subRes.data?.length > 0) {
      setActiveSubscriptions(subRes.data);
      if (!selectedSubId) setSelectedSubId(subRes.data[0].id);
    }
  };

  useEffect(() => {
    fetchData();
  }, [overdueOnly, statusFilter]);

  const handleGenerateInvoice = async (e) => {
    e.preventDefault();
    if (!selectedSubId) {
      notify.error('Please select an active subscription.');
      return;
    }
    if (!billingPeriodKey.trim()) {
      notify.error('Billing period key (e.g., 2026-11) is required.');
      return;
    }

    const res = await generateInvoice({
      subscription_id: parseInt(selectedSubId),
      billing_period_key: billingPeriodKey.trim(),
      due_date: dueDate,
    });

    if (res.success) {
      notify.success(`Invoice #${res.data?.id} generated successfully for period ${billingPeriodKey}.`);
      setShowGenerateModal(false);
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to generate invoice.';
      notify.error(errMsg);
    }
  };

  const handleStatusChange = async (id, nextStatus) => {
    const res = await updateInvoiceStatus(id, nextStatus);
    if (res.success) {
      notify.success(`Invoice #${id} transitioned to ${nextStatus}.`);
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to update status.';
      notify.error(errMsg);
    }
  };

  const statusBadge = (status) => {
    const styles = {
      draft: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
      confirmed: 'bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800',
      paid: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
    };
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase border tracking-wider shrink-0 ${styles[status] || styles.draft}`}>
        {status}
      </span>
    );
  };

  const statuses = ['', 'draft', 'confirmed', 'paid'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Recurring Invoices</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Period billing generation with automated tax calculations and double-billing defense
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition w-full sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Generate Period Invoice</span>
          </button>
        )}
      </div>

      {/* Filter Disclosure (< md collapsible, md+ inline) */}
      <div className="space-y-2">
        <div className="md:hidden flex flex-col gap-2">
          <button
            onClick={() => setFiltersOpen(!filtersOpen)}
            className="w-full flex items-center justify-between px-4 py-2.5 min-h-[44px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-200 shadow-xs"
          >
            <span className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Filter: {statusFilter ? statusFilter.toUpperCase() : 'ALL INVOICES'}</span>
            </span>
            {filtersOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        <div className={`${filtersOpen ? 'flex' : 'hidden'} md:flex flex-wrap items-center justify-between gap-3 pt-2 md:pt-0`}>
          <div className="flex flex-wrap items-center gap-2">
            {statuses.map((st) => (
              <button
                key={st}
                onClick={() => {
                  setStatusFilter(st);
                  setOverdueOnly(false);
                  setFiltersOpen(false);
                }}
                className={`px-3.5 py-2 min-h-[44px] rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                  !overdueOnly && statusFilter === st
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
                }`}
              >
                {st || 'All'}
              </button>
            ))}
          </div>

          <button
            onClick={() => setOverdueOnly(!overdueOnly)}
            className={`flex items-center justify-center gap-1.5 px-3.5 py-2 min-h-[44px] rounded-lg text-xs font-semibold uppercase tracking-wider transition border ${
              overdueOnly
                ? 'bg-rose-600 text-white border-rose-600'
                : 'bg-white dark:bg-slate-900 border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40'
            }`}
          >
            <AlertCircle className="w-4 h-4" />
            <span>Show Overdue Invoices</span>
          </button>
        </div>
      </div>

      {/* Structured Div Grid for md (>= 768px) and lg (>= 1280px) */}
      <div className="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden transition-colors">
        <div className="grid grid-cols-12 gap-4 px-5 py-3.5 bg-slate-50/70 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
          <div className="col-span-2">Invoice #</div>
          <div className="col-span-2">Billing Period</div>
          <div className="col-span-2">Net & Tax</div>
          <div className="col-span-2 text-right">Total Amount</div>
          <div className="col-span-1">Due Date</div>
          <div className="col-span-1">Status</div>
          <div className="col-span-2 text-right">Transitions</div>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {invoices.map((inv) => (
            <div key={inv.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 items-center hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
              <div className="col-span-2 font-bold font-mono text-xs text-slate-900 dark:text-white">INV-{inv.id}</div>
              <div className="col-span-2 font-medium text-slate-700 dark:text-slate-200">
                <span className="px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-xs font-mono">
                  {inv.billing_period_key}
                </span>
              </div>
              <div className="col-span-2 text-xs text-slate-500 dark:text-slate-400">
                <div>Net: ₹{Number(inv.subtotal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                <div>Tax: ₹{Number(inv.tax_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
              </div>
              <div className="col-span-2 text-right font-extrabold text-slate-900 dark:text-white text-base">
                ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div className="col-span-1 text-xs text-slate-600 dark:text-slate-400">{inv.due_date || 'N/A'}</div>
              <div className="col-span-1">{statusBadge(inv.status)}</div>
              <div className="col-span-2 text-right">
                <div className="flex items-center justify-end gap-1.5 flex-wrap">
                  {inv.status === 'draft' && (
                    <button
                      onClick={() => handleStatusChange(inv.id, 'confirmed')}
                      className="px-2.5 py-1 text-xs font-medium bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-md transition"
                    >
                      Confirm
                    </button>
                  )}
                  {inv.status === 'confirmed' && (
                    <button
                      onClick={() => handleStatusChange(inv.id, 'paid')}
                      className="px-2.5 py-1 text-xs font-medium bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-md transition"
                    >
                      Mark Paid
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Card View below md (< 768px, phone base & sm) with Full-Width Action Buttons */}
      <div className="md:hidden space-y-3">
        {invoices.map((inv) => (
          <div key={inv.id} className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-3 transition-colors">
            <div className="flex justify-between items-start gap-2">
              <div>
                <span className="font-mono font-bold text-xs text-slate-900 dark:text-white">INV-{inv.id}</span>
                <span className="text-xs ml-2 px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 font-mono text-slate-700 dark:text-slate-300">
                  {inv.billing_period_key}
                </span>
              </div>
              {statusBadge(inv.status)}
            </div>

            <div className="flex justify-between items-baseline pt-1">
              <span className="text-xs text-slate-500 dark:text-slate-400">Total with Tax</span>
              <span className="text-lg font-extrabold text-slate-900 dark:text-white">
                ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>

            <div className="text-xs text-slate-400 dark:text-slate-500 flex justify-between">
              <span>Net: ₹{Number(inv.subtotal).toLocaleString('en-IN')}</span>
              <span>Due: {inv.due_date || 'N/A'}</span>
            </div>

            {/* Actions as Full-Width Buttons */}
            {(inv.status === 'draft' || inv.status === 'confirmed') && (
              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-2">
                {inv.status === 'draft' && (
                  <button
                    onClick={() => handleStatusChange(inv.id, 'confirmed')}
                    className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-lg transition"
                  >
                    Confirm Invoice
                  </button>
                )}
                {inv.status === 'confirmed' && (
                  <button
                    onClick={() => handleStatusChange(inv.id, 'paid')}
                    className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-lg transition"
                  >
                    Mark Paid & Reconciled
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Generate Invoice Modal (Single column mobile, two column md+) */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-slate-200 dark:border-slate-800 my-auto space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Generate Periodic Invoice</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Generates snapshot invoice from active subscription lines. Double-billing for the same period is blocked at DB level.
            </p>
            <form onSubmit={handleGenerateInvoice} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Active Subscription
                </label>
                <select
                  value={selectedSubId}
                  onChange={(e) => setSelectedSubId(e.target.value)}
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                >
                  {activeSubscriptions.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.number} (Customer #{s.customer_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Billing Period Key
                  </label>
                  <input
                    type="text"
                    required
                    value={billingPeriodKey}
                    onChange={(e) => setBillingPeriodKey(e.target.value)}
                    placeholder="e.g. 2026-11"
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-mono"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Due Date
                  </label>
                  <input
                    type="date"
                    required
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition"
                >
                  Generate Invoice
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
