import React, { useEffect, useState } from 'react';
import { 
  getPayments, 
  createPayment, 
  getOutstandingInvoices, 
  getCurrentUser 
} from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { CreditCard, Plus, Clock } from 'lucide-react';

export default function PaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [outstandingInvoices, setOutstandingInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const user = getCurrentUser();

  // Record Payment Modal State
  const [showModal, setShowModal] = useState(false);
  const [selectedInvoiceId, setSelectedInvoiceId] = useState('');
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('bank_transfer');
  const [paymentDate, setPaymentDate] = useState(new Date().toISOString().split('T')[0]);
  const [reference, setReference] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    const [pRes, oRes] = await Promise.all([
      getPayments(),
      getOutstandingInvoices(),
    ]);
    setLoading(false);

    if (pRes.success) setPayments(pRes.data || []);
    else setError(pRes.error || 'Failed to fetch payment ledger');

    if (oRes.success && oRes.data?.length > 0) {
      setOutstandingInvoices(oRes.data);
      if (!selectedInvoiceId) {
        setSelectedInvoiceId(oRes.data[0].id);
        setPaymentAmount(oRes.data[0].total);
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRecordPayment = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Layer 1 Client Check
    const amountNum = parseFloat(paymentAmount);
    if (isNaN(amountNum) || amountNum <= 0) {
      setError('Payment amount must be strictly greater than 0 (Layer 1 Defense).');
      return;
    }
    if (!selectedInvoiceId) {
      setError('Please choose an invoice to apply payment.');
      return;
    }

    const res = await createPayment({
      invoice_id: parseInt(selectedInvoiceId),
      amount: amountNum,
      method: paymentMethod,
      payment_date: paymentDate,
      reference: reference.trim() || undefined,
    });

    if (res.success) {
      setSuccess(`Payment of ₹${amountNum.toLocaleString('en-IN', { minimumFractionDigits: 2 })} recorded successfully!`);
      setShowModal(false);
      fetchData();
    } else {
      setError(res.error || 'Payment rejected.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Payments & Ledger</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Settlement records with strict positive amount validation and invoice linking
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition w-full sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            <span>Record Payment</span>
          </button>
        )}
      </div>

      <AlertBanner type="error" message={error} onClose={() => setError('')} />
      <AlertBanner type="success" message={success} onClose={() => setSuccess('')} />

      {/* Outstanding Invoices Section */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-600 dark:text-amber-400" />
          <span>Outstanding Invoices Awaiting Settlement ({outstandingInvoices.length})</span>
        </h2>

        {outstandingInvoices.length === 0 ? (
          <div className="p-6 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl text-center text-sm text-slate-500 dark:text-slate-400 transition-colors">
            No outstanding confirmed invoices. All accounts are settled!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {outstandingInvoices.map((inv) => (
              <div 
                key={inv.id} 
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/20 dark:bg-amber-950/20 shadow-xs flex flex-col justify-between transition-colors"
              >
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
                    <span className="font-mono font-bold text-slate-800 dark:text-slate-200">INV-#{inv.id}</span>
                    <span>Period: {inv.billing_period_key}</span>
                  </div>
                  <div className="text-xl sm:text-2xl font-extrabold text-slate-900 dark:text-white mt-2">
                    ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mt-1">Due Date: {inv.due_date || 'Immediate'}</div>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-100 dark:border-amber-900/40 flex justify-end">
                  <button
                    onClick={() => {
                      setSelectedInvoiceId(inv.id);
                      setPaymentAmount(inv.total);
                      setShowModal(true);
                    }}
                    className="w-full sm:w-auto min-h-[44px] flex items-center justify-center px-4 py-2 text-xs font-bold uppercase tracking-wider bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-xs transition"
                  >
                    Pay Invoice
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Payment History Section */}
      <div className="space-y-4 pt-4">
        <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          <span>Historical Payments Log</span>
        </h2>

        {/* Structured Div Grid for md (>= 768px) and lg (>= 1280px) */}
        <div className="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden transition-colors">
          <div className="grid grid-cols-12 gap-4 px-5 py-3.5 bg-slate-50/70 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
            <div className="col-span-2">ID</div>
            <div className="col-span-3">Applied Invoice</div>
            <div className="col-span-2">Method</div>
            <div className="col-span-2">Date</div>
            <div className="col-span-3 text-right">Settled Amount</div>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {payments.map((p) => (
              <div key={p.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 items-center hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
                <div className="col-span-2 font-mono text-xs text-slate-400 dark:text-slate-500">PAY-{p.id}</div>
                <div className="col-span-3 font-semibold text-slate-800 dark:text-slate-200">INV-#{p.invoice_id}</div>
                <div className="col-span-2 capitalize text-xs">
                  <span className="px-2.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium">
                    {p.method.replace('_', ' ')}
                  </span>
                </div>
                <div className="col-span-2 text-xs text-slate-500 dark:text-slate-400">{p.payment_date}</div>
                <div className="col-span-3 text-right font-extrabold text-emerald-700 dark:text-emerald-400 text-base">
                  ₹{Number(p.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card View below md (< 768px, phone base & sm) */}
        <div className="md:hidden space-y-3">
          {payments.map((p) => (
            <div key={p.id} className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs flex justify-between items-center transition-colors">
              <div className="min-w-0">
                <div className="font-semibold text-sm text-slate-900 dark:text-white">INV-#{p.invoice_id}</div>
                <div className="text-xs text-slate-400 dark:text-slate-500 capitalize truncate">
                  {p.method.replace('_', ' ')} • {p.payment_date}
                </div>
              </div>
              <div className="text-right font-extrabold text-emerald-700 dark:text-emerald-400 text-base shrink-0 pl-3">
                ₹{Number(p.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Record Payment Modal (Single column mobile, two column md+) */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-slate-200 dark:border-slate-800 my-auto space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Record Settlement Payment</h3>
            <form onSubmit={handleRecordPayment} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Select Target Invoice
                </label>
                <select
                  value={selectedInvoiceId}
                  onChange={(e) => {
                    setSelectedInvoiceId(e.target.value);
                    const inv = outstandingInvoices.find((x) => x.id === parseInt(e.target.value));
                    if (inv) setPaymentAmount(inv.total);
                  }}
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                >
                  {outstandingInvoices.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      INV-#{inv.id} (₹{Number(inv.total).toLocaleString('en-IN')})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Amount (₹) — Must be &gt; 0
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  value={paymentAmount}
                  onChange={(e) => setPaymentAmount(e.target.value)}
                  placeholder="e.g. 1500.00"
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg font-bold text-slate-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Method
                  </label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                  >
                    <option value="bank_transfer">Bank Transfer / NEFT</option>
                    <option value="upi">UPI / QR</option>
                    <option value="card">Credit / Debit Card</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Date
                  </label>
                  <input
                    type="date"
                    required
                    value={paymentDate}
                    onChange={(e) => setPaymentDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Reference / Transaction ID
                </label>
                <input
                  type="text"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  placeholder="e.g. UTR-98721634"
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                />
              </div>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition"
                >
                  Confirm Payment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
