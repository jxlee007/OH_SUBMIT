import React, { useEffect, useState } from 'react';
import { 
  getPayments, 
  createPayment, 
  getOutstandingInvoices, 
  getCurrentUser 
} from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { CreditCard, Plus, CheckCircle, Clock, ArrowRight } from 'lucide-react';

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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Payments & Ledger</h1>
          <p className="text-sm text-slate-500 mt-1">
            Settlement records with strict positive amount validation and invoice linking
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition"
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
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <Clock className="w-5 h-5 text-amber-600" />
          <span>Outstanding Invoices Awaiting Settlement ({outstandingInvoices.length})</span>
        </h2>

        {outstandingInvoices.length === 0 ? (
          <div className="p-6 bg-white border border-slate-200 rounded-2xl text-center text-sm text-slate-500">
            No outstanding confirmed invoices. All accounts are settled!
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {outstandingInvoices.map((inv) => (
              <div key={inv.id} className="bg-white p-5 rounded-2xl border border-amber-200 bg-amber-50/20 shadow-xs flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between text-xs text-slate-500 mb-1">
                    <span className="font-mono font-bold text-slate-800">INV-#{inv.id}</span>
                    <span>Period: {inv.billing_period_key}</span>
                  </div>
                  <div className="text-xl font-extrabold text-slate-900 mt-2">
                    ₹{Number(inv.total).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-xs text-slate-500 mt-1">Due Date: {inv.due_date || 'Immediate'}</div>
                </div>
                <div className="mt-4 pt-3 border-t border-amber-100 flex justify-end">
                  <button
                    onClick={() => {
                      setSelectedInvoiceId(inv.id);
                      setPaymentAmount(inv.total);
                      setShowModal(true);
                    }}
                    className="px-3 py-1 text-xs font-semibold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-2xs"
                  >
                    Pay Invoice
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Payment History Table */}
      <div className="space-y-4 pt-4">
        <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
          <CreditCard className="w-5 h-5 text-indigo-600" />
          <span>Historical Payments Log</span>
        </h2>

        {/* 768px / 1280px Table */}
        <div className="hidden sm:block bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/70 border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3.5">ID</th>
                <th className="px-5 py-3.5">Applied Invoice</th>
                <th className="px-5 py-3.5">Method</th>
                <th className="px-5 py-3.5">Date</th>
                <th className="px-5 py-3.5 text-right">Settled Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {payments.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/50 transition">
                  <td className="px-5 py-3.5 font-mono text-xs text-slate-400">PAY-{p.id}</td>
                  <td className="px-5 py-3.5 font-semibold text-slate-800">INV-#{p.invoice_id}</td>
                  <td className="px-5 py-3.5 capitalize text-xs">
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium">
                      {p.method.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-xs text-slate-500">{p.payment_date}</td>
                  <td className="px-5 py-3.5 text-right font-extrabold text-emerald-700">
                    ₹{Number(p.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 375px Mobile View */}
        <div className="sm:hidden space-y-3">
          {payments.map((p) => (
            <div key={p.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs flex justify-between items-center">
              <div>
                <div className="font-semibold text-sm text-slate-900">INV-#{p.invoice_id}</div>
                <div className="text-xs text-slate-400 capitalize">{p.method.replace('_', ' ')} • {p.payment_date}</div>
              </div>
              <div className="text-right font-extrabold text-emerald-700">
                ₹{Number(p.amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Record Payment Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Record Settlement Payment</h3>
            <form onSubmit={handleRecordPayment} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Select Target Invoice
                </label>
                <select
                  value={selectedInvoiceId}
                  onChange={(e) => {
                    setSelectedInvoiceId(e.target.value);
                    const inv = outstandingInvoices.find((x) => x.id === parseInt(e.target.value));
                    if (inv) setPaymentAmount(inv.total);
                  }}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                >
                  {outstandingInvoices.map((inv) => (
                    <option key={inv.id} value={inv.id}>
                      INV-#{inv.id} (₹{Number(inv.total).toLocaleString('en-IN')})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
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
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-bold text-slate-900"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Method</label>
                  <select
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                  >
                    <option value="bank_transfer">Bank Transfer / NEFT</option>
                    <option value="upi">UPI / QR</option>
                    <option value="card">Credit / Debit Card</option>
                    <option value="cheque">Cheque</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Date</label>
                  <input
                    type="date"
                    required
                    value={paymentDate}
                    onChange={(e) => setPaymentDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                  Reference / Transaction ID
                </label>
                <input
                  type="text"
                  value={reference}
                  onChange={(e) => setReference(e.target.value)}
                  placeholder="e.g. UTR-98721634"
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                />
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
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
