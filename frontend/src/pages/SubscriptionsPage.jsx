import React, { useEffect, useState } from 'react';
import { 
  getSubscriptions, 
  createSubscription, 
  updateSubscriptionStatus, 
  getPlans, 
  getProducts, 
  getCurrentUser 
} from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { Repeat, Plus, CheckCircle, ArrowRight, XCircle, FileSpreadsheet } from 'lucide-react';

export default function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [plans, setPlans] = useState([]);
  const [products, setProducts] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const user = getCurrentUser();

  // Create Subscription Form State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedPlanId, setSelectedPlanId] = useState('');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [paymentTerms, setPaymentTerms] = useState('Net 15');
  const [selectedProductId, setSelectedProductId] = useState('');
  const [lineQuantity, setLineQuantity] = useState(1);
  const [lineUnitPrice, setLineUnitPrice] = useState('1000.00');
  const [lineTaxRate, setLineTaxRate] = useState('18.00');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    const [subRes, planRes, prodRes] = await Promise.all([
      getSubscriptions(statusFilter),
      getPlans(),
      getProducts(),
    ]);
    setLoading(false);

    if (subRes.success) setSubscriptions(subRes.data || []);
    else setError(subRes.error || 'Failed to fetch subscriptions');

    if (planRes.success && planRes.data?.length > 0) {
      setPlans(planRes.data);
      if (!selectedPlanId) setSelectedPlanId(planRes.data[0].id);
    }

    if (prodRes.success && prodRes.data?.length > 0) {
      setProducts(prodRes.data);
      if (!selectedProductId) {
        setSelectedProductId(prodRes.data[0].id);
        setLineUnitPrice(prodRes.data[0].sales_price);
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, [statusFilter]);

  const handleStatusTransition = async (id, nextStatus) => {
    setError('');
    setSuccess('');
    const res = await updateSubscriptionStatus(id, nextStatus);
    if (res.success) {
      setSuccess(`Subscription #${id} successfully transitioned to ${nextStatus}.`);
      fetchData();
    } else {
      setError(res.error || 'Failed to transition subscription status.');
    }
  };

  const handleCreateSubscription = async (e) => {
    e.preventDefault();
    if (!selectedPlanId) {
      setError('Please select a valid plan.');
      return;
    }

    const payload = {
      customer_id: user?.id || 3, // fallback to customer seed id
      plan_id: parseInt(selectedPlanId),
      start_date: startDate,
      payment_terms: paymentTerms,
      lines: [
        {
          product_id: parseInt(selectedProductId),
          quantity: parseInt(lineQuantity) || 1,
          unit_price: parseFloat(lineUnitPrice) || 0,
          tax_rate: parseFloat(lineTaxRate) || 0,
        },
      ],
    };

    const res = await createSubscription(payload);
    if (res.success) {
      setSuccess(`Subscription ${res.data?.number} created in Draft.`);
      setShowCreateModal(false);
      fetchData();
    } else {
      setError(res.error || 'Failed to create subscription.');
    }
  };

  const statusBadge = (status) => {
    const styles = {
      draft: 'bg-slate-100 text-slate-700 border-slate-200',
      quotation: 'bg-sky-50 text-sky-800 border-sky-200',
      confirmed: 'bg-amber-50 text-amber-800 border-amber-200',
      active: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      closed: 'bg-rose-50 text-rose-800 border-rose-200',
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
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Subscriptions</h1>
          <p className="text-sm text-slate-500 mt-1">
            Strict State Machine: Draft → Quotation → Confirmed → Active → Closed
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition"
          >
            <Plus className="w-4 h-4" />
            <span>New Subscription</span>
          </button>
        )}
      </div>

      <AlertBanner type="error" message={error} onClose={() => setError('')} />
      <AlertBanner type="success" message={success} onClose={() => setSuccess('')} />

      {/* Filter Tabs */}
      <div className="flex flex-wrap items-center gap-2">
        {['', 'draft', 'quotation', 'confirmed', 'active', 'closed'].map((st) => (
          <button
            key={st}
            onClick={() => setStatusFilter(st)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
              statusFilter === st
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {st ? st : 'All Statuses'}
          </button>
        ))}
      </div>

      {/* Table (Responsive 768px / 1280px) */}
      <div className="hidden sm:block bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50/70 border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
            <tr>
              <th className="px-5 py-3.5">Number</th>
              <th className="px-5 py-3.5">Customer / Terms</th>
              <th className="px-5 py-3.5">Start Date</th>
              <th className="px-5 py-3.5">Lifecycle State</th>
              <th className="px-5 py-3.5 text-right">Allowed State Transitions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {subscriptions.map((sub) => (
              <tr key={sub.id} className="hover:bg-slate-50/50 transition">
                <td className="px-5 py-3.5 font-bold text-slate-900 font-mono text-xs">{sub.number}</td>
                <td className="px-5 py-3.5">
                  <div className="text-slate-900 font-medium">Customer #{sub.customer_id}</div>
                  <div className="text-xs text-slate-400">{sub.payment_terms || 'Standard'}</div>
                </td>
                <td className="px-5 py-3.5 text-xs text-slate-600">{sub.start_date}</td>
                <td className="px-5 py-3.5">{statusBadge(sub.status)}</td>
                <td className="px-5 py-3.5 text-right">
                  <div className="flex items-center justify-end gap-1.5">
                    {sub.status === 'draft' && (
                      <button
                        onClick={() => handleStatusTransition(sub.id, 'quotation')}
                        className="px-2.5 py-1 text-xs font-medium bg-sky-50 hover:bg-sky-100 text-sky-800 border border-sky-200 rounded-md transition"
                        title="Send Quotation to Customer"
                      >
                        Send Quotation
                      </button>
                    )}
                    {sub.status === 'quotation' && (
                      <button
                        onClick={() => handleStatusTransition(sub.id, 'confirmed')}
                        className="px-2.5 py-1 text-xs font-medium bg-amber-50 hover:bg-amber-100 text-amber-800 border border-amber-200 rounded-md transition"
                        title="Customer Confirms Quotation"
                      >
                        Confirm
                      </button>
                    )}
                    {sub.status === 'confirmed' && (
                      <button
                        onClick={() => handleStatusTransition(sub.id, 'active')}
                        className="px-2.5 py-1 text-xs font-medium bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 rounded-md transition"
                        title="Activate Subscription"
                      >
                        Activate
                      </button>
                    )}
                    {sub.status !== 'closed' && (
                      <button
                        onClick={() => handleStatusTransition(sub.id, 'closed')}
                        className="px-2 py-1 text-xs font-medium text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-md transition"
                        title="Close Subscription"
                      >
                        Close
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
        {subscriptions.map((sub) => (
          <div key={sub.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-3">
            <div className="flex justify-between items-center">
              <span className="font-mono font-bold text-xs text-slate-900">{sub.number}</span>
              {statusBadge(sub.status)}
            </div>
            <div className="text-xs text-slate-500">
              <div>Customer #{sub.customer_id} • Starts {sub.start_date}</div>
            </div>
            <div className="pt-2 border-t border-slate-100 flex justify-end gap-2">
              {sub.status === 'draft' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'quotation')}
                  className="px-3 py-1 text-xs font-semibold bg-sky-100 text-sky-800 rounded-md"
                >
                  Send Quotation
                </button>
              )}
              {sub.status === 'quotation' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'confirmed')}
                  className="px-3 py-1 text-xs font-semibold bg-amber-100 text-amber-800 rounded-md"
                >
                  Confirm
                </button>
              )}
              {sub.status === 'confirmed' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'active')}
                  className="px-3 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded-md"
                >
                  Activate
                </button>
              )}
              {sub.status !== 'closed' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'closed')}
                  className="px-2.5 py-1 text-xs font-medium text-rose-600 border border-rose-200 rounded-md"
                >
                  Close
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-100 space-y-4">
            <h3 className="text-lg font-bold text-slate-900">Create Subscription (Draft)</h3>
            <form onSubmit={handleCreateSubscription} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Select Plan</label>
                <select
                  value={selectedPlanId}
                  onChange={(e) => setSelectedPlanId(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                >
                  {plans.map((pl) => (
                    <option key={pl.id} value={pl.id}>
                      {pl.name} (₹{Number(pl.price).toLocaleString('en-IN')} / {pl.billing_period})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Payment Terms</label>
                  <input
                    type="text"
                    value={paymentTerms}
                    onChange={(e) => setPaymentTerms(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                  />
                </div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                <div className="text-xs font-bold text-slate-700 uppercase">Subscription Line Item</div>
                <div>
                  <label className="block text-xs text-slate-600 mb-1">Product</label>
                  <select
                    value={selectedProductId}
                    onChange={(e) => {
                      setSelectedProductId(e.target.value);
                      const p = products.find((x) => x.id === parseInt(e.target.value));
                      if (p) setLineUnitPrice(p.sales_price);
                    }}
                    className="w-full px-3 py-1.5 text-sm border border-slate-300 rounded-lg bg-white"
                  >
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={lineQuantity}
                      onChange={(e) => setLineQuantity(e.target.value)}
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Price (₹)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={lineUnitPrice}
                      onChange={(e) => setLineUnitPrice(e.target.value)}
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg bg-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-600 mb-1">Tax (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={lineTaxRate}
                      onChange={(e) => setLineTaxRate(e.target.value)}
                      className="w-full px-2 py-1.5 text-sm border border-slate-300 rounded-lg bg-white"
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
                >
                  Create Subscription
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
