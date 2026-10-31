import React, { useEffect, useState } from 'react';
import { 
  getSubscriptions, 
  createSubscription, 
  updateSubscriptionStatus, 
  getPlans, 
  getProducts, 
  getCurrentUser 
} from '../services/api';
import notify from '../services/notify';
import { Repeat, Plus, Filter, ChevronDown, ChevronUp } from 'lucide-react';

export default function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [plans, setPlans] = useState([]);
  const [products, setProducts] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [filtersOpen, setFiltersOpen] = useState(false);
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
    const [subRes, planRes, prodRes] = await Promise.all([
      getSubscriptions(statusFilter),
      getPlans(),
      getProducts(),
    ]);
    setLoading(false);

    if (subRes.success) setSubscriptions(subRes.data || []);
    else notify.error(subRes.error || 'Failed to fetch subscriptions');

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
    const res = await updateSubscriptionStatus(id, nextStatus);
    if (res.success) {
      notify.success(`Subscription #${id} successfully transitioned to ${nextStatus}.`);
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to transition subscription status.';
      notify.error(errMsg);
    }
  };

  const handleCreateSubscription = async (e) => {
    e.preventDefault();
    if (!selectedPlanId) {
      notify.error('Please select a valid plan.');
      return;
    }

    const payload = {
      customer_id: user?.id || 3,
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
      notify.success(`Subscription ${res.data?.number} created in Draft.`);
      setShowCreateModal(false);
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to create subscription.';
      notify.error(errMsg);
    }
  };

  const statusBadge = (status) => {
    const styles = {
      draft: 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700',
      quotation: 'bg-sky-50 dark:bg-sky-950/60 text-sky-800 dark:text-sky-300 border-sky-200 dark:border-sky-800',
      confirmed: 'bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-800',
      active: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800',
      closed: 'bg-rose-50 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 border-rose-200 dark:border-rose-800',
    };
    return (
      <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold uppercase border tracking-wider shrink-0 ${styles[status] || styles.draft}`}>
        {status}
      </span>
    );
  };

  const statuses = ['', 'draft', 'quotation', 'confirmed', 'active', 'closed'];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Subscriptions</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Strict State Machine: Draft → Quotation → Confirmed → Active → Closed
          </p>
        </div>
        {user?.role !== 'customer' && (
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center justify-center gap-1.5 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition w-full sm:w-auto"
          >
            <Plus className="w-4 h-4" />
            <span>New Subscription</span>
          </button>
        )}
      </div>

      {/* Filter Disclosure (< md collapsible, md+ inline) */}
      <div className="space-y-2">
        <div className="md:hidden">
          <button
            onClick={() => setFiltersOpen(!filtersOpen)}
            className="w-full flex items-center justify-between px-4 py-2.5 min-h-[44px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm font-medium text-slate-700 dark:text-slate-200 shadow-xs"
          >
            <span className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Filter: {statusFilter ? statusFilter.toUpperCase() : 'ALL STATUSES'}</span>
            </span>
            {filtersOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        <div className={`${filtersOpen ? 'flex' : 'hidden'} md:flex flex-wrap items-center gap-2 pt-2 md:pt-0`}>
          {statuses.map((st) => (
            <button
              key={st}
              onClick={() => {
                setStatusFilter(st);
                setFiltersOpen(false);
              }}
              className={`px-3.5 py-2 min-h-[44px] rounded-lg text-xs font-semibold uppercase tracking-wider transition ${
                statusFilter === st
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800'
              }`}
            >
              {st ? st : 'All Statuses'}
            </button>
          ))}
        </div>
      </div>

      {/* Structured Div Grid for md (>= 768px) and lg (>= 1280px) */}
      <div className="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden transition-colors">
        <div className="grid grid-cols-12 gap-4 px-5 py-3.5 bg-slate-50/70 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
          <div className="col-span-2">Number</div>
          <div className="col-span-3">Customer / Terms</div>
          <div className="col-span-2">Start Date</div>
          <div className="col-span-2">Lifecycle State</div>
          <div className="col-span-3 text-right">Allowed Transitions</div>
        </div>
        <div className="divide-y divide-slate-100 dark:divide-slate-800">
          {subscriptions.map((sub) => (
            <div key={sub.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 items-center hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
              <div className="col-span-2 font-bold text-slate-900 dark:text-white font-mono text-xs truncate">
                {sub.number}
              </div>
              <div className="col-span-3">
                <div className="text-slate-900 dark:text-white font-medium text-sm">Customer #{sub.customer_id}</div>
                <div className="text-xs text-slate-400 dark:text-slate-500">{sub.payment_terms || 'Standard'}</div>
              </div>
              <div className="col-span-2 text-xs text-slate-600 dark:text-slate-400">{sub.start_date}</div>
              <div className="col-span-2">{statusBadge(sub.status)}</div>
              <div className="col-span-3 text-right">
                <div className="flex items-center justify-end gap-1.5 flex-wrap">
                  {sub.status === 'draft' && (
                    <button
                      onClick={() => handleStatusTransition(sub.id, 'quotation')}
                      className="px-2.5 py-1 text-xs font-medium bg-sky-50 dark:bg-sky-950/60 hover:bg-sky-100 dark:hover:bg-sky-900/60 text-sky-800 dark:text-sky-300 border border-sky-200 dark:border-sky-800 rounded-md transition"
                    >
                      Send Quotation
                    </button>
                  )}
                  {sub.status === 'quotation' && (
                    <button
                      onClick={() => handleStatusTransition(sub.id, 'confirmed')}
                      className="px-2.5 py-1 text-xs font-medium bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-md transition"
                    >
                      Confirm
                    </button>
                  )}
                  {sub.status === 'confirmed' && (
                    <button
                      onClick={() => handleStatusTransition(sub.id, 'active')}
                      className="px-2.5 py-1 text-xs font-medium bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-md transition"
                    >
                      Activate
                    </button>
                  )}
                  {sub.status !== 'closed' && (
                    <button
                      onClick={() => handleStatusTransition(sub.id, 'closed')}
                      className="px-2 py-1 text-xs font-medium text-slate-500 hover:text-rose-600 dark:text-slate-400 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-md transition"
                    >
                      Close
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
        {subscriptions.map((sub) => (
          <div key={sub.id} className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-3 transition-colors">
            <div className="flex justify-between items-start gap-2">
              <span className="font-mono font-bold text-xs text-slate-900 dark:text-white break-all">
                {sub.number}
              </span>
              {statusBadge(sub.status)}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 space-y-0.5">
              <div>Customer #{sub.customer_id} • Terms: {sub.payment_terms || 'Standard'}</div>
              <div>Starts: {sub.start_date}</div>
            </div>

            {/* Actions as Full-Width Buttons (min 44px touch target) */}
            <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex flex-col gap-2">
              {sub.status === 'draft' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'quotation')}
                  className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold bg-sky-50 dark:bg-sky-950/60 hover:bg-sky-100 dark:hover:bg-sky-900/60 text-sky-800 dark:text-sky-300 border border-sky-200 dark:border-sky-800 rounded-lg transition"
                >
                  Send Quotation
                </button>
              )}
              {sub.status === 'quotation' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'confirmed')}
                  className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800 rounded-lg transition"
                >
                  Confirm Quotation
                </button>
              )}
              {sub.status === 'confirmed' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'active')}
                  className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800 rounded-lg transition"
                >
                  Activate Subscription
                </button>
              )}
              {sub.status !== 'closed' && (
                <button
                  onClick={() => handleStatusTransition(sub.id, 'closed')}
                  className="w-full min-h-[44px] flex items-center justify-center px-4 py-2 text-sm font-semibold text-rose-600 dark:text-rose-400 bg-rose-50/50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900/60 rounded-lg hover:bg-rose-100 transition"
                >
                  Close Subscription
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal (Single column mobile, two column md+) */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-slate-200 dark:border-slate-800 my-auto space-y-4">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white">Create Subscription (Draft)</h3>
            <form onSubmit={handleCreateSubscription} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Select Plan
                </label>
                <select
                  value={selectedPlanId}
                  onChange={(e) => setSelectedPlanId(e.target.value)}
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                >
                  {plans.map((pl) => (
                    <option key={pl.id} value={pl.id}>
                      {pl.name} (₹{Number(pl.price).toLocaleString('en-IN')} / {pl.billing_period})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Start Date
                  </label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Payment Terms
                  </label>
                  <input
                    type="text"
                    value={paymentTerms}
                    onChange={(e) => setPaymentTerms(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  />
                </div>
              </div>

              <div className="p-3.5 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl space-y-3">
                <div className="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase">
                  Subscription Line Item
                </div>
                <div>
                  <label className="block text-xs text-slate-600 dark:text-slate-400 mb-1">Product</label>
                  <select
                    value={selectedProductId}
                    onChange={(e) => {
                      setSelectedProductId(e.target.value);
                      const p = products.find((x) => x.id === parseInt(e.target.value));
                      if (p) setLineUnitPrice(p.sales_price);
                    }}
                    className="w-full px-3.5 py-2 min-h-[44px] text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  >
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs text-slate-600 dark:text-slate-400 mb-1">Qty</label>
                    <input
                      type="number"
                      min="1"
                      value={lineQuantity}
                      onChange={(e) => setLineQuantity(e.target.value)}
                      className="w-full px-3 py-2 min-h-[44px] text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-600 dark:text-slate-400 mb-1">Price (₹)</label>
                    <input
                      type="number"
                      step="0.01"
                      value={lineUnitPrice}
                      onChange={(e) => setLineUnitPrice(e.target.value)}
                      className="w-full px-3 py-2 min-h-[44px] text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-slate-600 dark:text-slate-400 mb-1">Tax (%)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={lineTaxRate}
                      onChange={(e) => setLineTaxRate(e.target.value)}
                      className="w-full px-3 py-2 min-h-[44px] text-sm bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition"
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
