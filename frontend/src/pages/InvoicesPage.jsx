import React, { useEffect, useState } from 'react';
import { 
  getInvoices, 
  generateInvoice, 
  updateInvoiceStatus, 
  getSubscriptions, 
  getCurrentUser 
} from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { Receipt, Plus, AlertCircle, CheckCircle, FileText, Calendar } from 'lucide-react';

export default function InvoicesPage() {
  const [invoices, setInvoices] = useState([]);
  const [activeSubscriptions, setActiveSubscriptions] = useState([]);
  const [overdueOnly, setOverdueOnly] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const user = getCurrentUser();

  // Generate Invoice Form
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [selectedSubId, setSelectedSubId] = useState('');
  const [billingPeriodKey, setBillingPeriodKey] = useState('2026-11');
  const [dueDate, setDueDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchData = async () => {
    setLoading(true);
    setError('');
    const [invRes, subRes] = await Promise.all([
      getInvoices(overdueOnly, statusFilter),
      getSubscriptions('active'),
    ]);
    setLoading(false);

    if (invRes.success) setInvoices(invRes.data || []);
    else setError(invRes.error || 'Failed to fetch invoices');

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
      setError('Please select an active subscription.');
      return;
    }
    if (!billingPeriodKey.trim()) {
      setError('Billing period key (e.g., 2026-11) is required.');
      return;
    }

    const res = await generateInvoice({
      subscription_id: parseInt(selectedSubId),
      billing_period_key: billingPeriodKey.trim(),
      due_date: dueDate,
    });

    if (res.success) {
      setSuccess(`Invoice #${res.data?.id} generated successfully for period ${billingPeriodKey}.`);
      setShowGenerateModal(false);
      fetchData();
    } else {
      // Highlights double-billing 409 prevention!
      setError(res.error || 'Failed to generate invoice.');
    }
  };

  const handleStatusChange = async (id, nextStatus) => {
    setError('');
    setSuccess('');
    const res = await updateInvoiceStatus(id, nextStatus);
    if (res.success) {
      setSuccess(`Invoice #${id} transitioned to ${nextStatus}.`);
      fetchData();
    } else {
      setError(res.error || 'Failed to update status.');
    }
  };

  const statusBadge = (status) => {
    const styles = {
      draft: 'bg-slate-100 text-slate-700 border-slate-200',
      confirmed: 'bg-amber-50 text-amber-800 border-amber-200',
      paid: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    };
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase border tracking-wider ${styles[status] || styles.draft}`}>
        {status}
      </span>
    );
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Recurring Invoices</h1>
          <p className="text-sm text-slate-500 mt-1">
            Period billing generation with automated tax calculations and double-billing defense
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowGenerateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>Generate Period Invoice</span>
          </button>
        )}
      </div>

      <AlertBanner type="error" message={error} onClose={() => setError('')} />
      <AlertBanner type="success" message={success} onClose={() => setSuccess('')} />

      {/* Filter Options */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          {['', 'draft', 'confirmed', 'paid'].map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setOverdueOnly(false);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                !overdueOnly && statusFilter === st
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {st || 'All'}
            </button>
          ))}
        </div>

        <button
          onClick={() => setOverdueOnly(!overdueOnly)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition border ${
            overdueOnly
              ? 'bg-rose-600 text-white border-rose-600'
              : 'bg-white border-rose-200 text-rose-700 hover:bg-rose-50'
          }`}
        >
          <AlertCircle className="w-3.5 h-3.5" />
          <span>Show Overdue Invoices</span>
        </button>
      </div>

      {/* Desktop Table (768px / 1280px) */}
      <div className="hidden sm:block bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50/70 border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-5 py-3.5">Invoice #</th>
              <th className="px-5 py-3.5">Billing Period</th>
              <th className="px-5 py-3.5">Net & Tax</th>
              <th className="px-5 py-3.5 text-right">Total Amount</th>
              <th className="px-5 py-3.5">Due Date</th>
              <th className="px-5 py-3.5">Status</th>
              <th className="px-5 py-3.5 text-right">Transitions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {invoices.map((inv) => (
              <tr key={inv.id} className="hover:bg-slate-50/50 transition">
                <td className="px-5 py-3.5 font-bold font-mono text-xs text-slate-900">INV-{inv.id}</td>
                <td className="px-5 py-3.5 font-medium text-slate-700">
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-xs font-mono">
                    {inv.billing_period_key}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-xs text-slate-500">
                  <div>Net: ₹{Number(inv.subtotal).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                  <div>Tax: ₹{Number(inv.tax_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
                </td>
                <td className="px-5 py-3.5 text-right font-extrabold text-slate-900 text-base">
                  ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </td>
                <td className="px-5 py-3.5 text-xs text-slate-600">{inv.due_date || 'N/A'}</td>
                <td className="px-5 py-3.5">{statusBadge(inv.status)}</td>
                <td className="px-5 py-3.5 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    {inv.status === 'draft' && (
                      <button
                        onClick={() => handleStatusChange(inv.id, 'confirmed')}
                        className="px-2.5 py-1 text-xs font-medium bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-md transition"
                      >
                        Confirm
                      </button>
                    )}
                    {inv.status === 'confirmed' && (
                      <button
                        onClick={() => handleStatusChange(inv.id, 'paid')}
                        className="px-2.5 py-1 text-xs font-medium bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-md transition"
                      >
                        Mark Paid
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 375px Mobile View */}
      <div className="sm:hidden space-y-3">
        {invoices.map((inv) => (
          <div key={inv.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-mono font-bold text-xs text-slate-900">INV-{inv.id} ({inv.billing_period_key})</span>
              {statusBadge(inv.status)}
            </div>
            <div className="flex justify-between items-baseline pt-1">
              <span className="text-xs text-slate-500">Total with Tax</span>
              <span className="text-base font-extrabold text-slate-900">
                ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="text-xs text-slate-400">Due: {inv.due_date || 'N/A'}</div>
            <div className="pt-2 border-t border-slate-100 flex justify-end gap-2">
              {inv.status === 'draft' && (
                <button
                  onClick={() => handleStatusChange(inv.id, 'confirmed')}
                  className="px-3 py-1 text-xs font-semibold bg-amber-100 text-amber-800 rounded-md"
                >
                  Confirm
                </button>
              )}
              {inv.status === 'confirmed' && (
                <button
                  onClick={() => handleStatusChange(inv.id, 'paid')}
                  className="px-3 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-md"
                >
                  Mark Paid
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Generate Invoice Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Generate Periodic Invoice</h3>
            <p className="text-xs text-slate-500">
              Generates snapshot invoice from active subscription lines. Double-billing for the same period is blocked at DB level.
            </p>
            <form onSubmit={handleGenerateInvoice} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Active Subscription
                </label>
                <select
                  value={selectedSubId}
                  onChange={(e) => setSelectedSubId(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                >
                  {activeSubscriptions.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.number} (Customer #{s.customer_id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Billing Period Key (Unique per subscription)
                </label>
                <input
                  type="text"
                  required
                  value={billingPeriodKey}
                  onChange={(e) => setBillingPeriodKey(e.target.value)}
                  placeholder="e.g. 2026-11 or 2026-W44"
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Payment Due Date
                </label>
                <input
                  type="date"
                  required
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
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
