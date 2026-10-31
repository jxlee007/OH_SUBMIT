import React, { useEffect, useState } from 'react';
import { getProducts, createProduct, getPlans, createPlan, getCurrentUser } from '../services/api';
import AlertBanner from '../components/AlertBanner';
import notify from '../services/notify';
import { Package, Plus, Calendar } from 'lucide-react';

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const user = getCurrentUser();

  // Create Product Form State
  const [showProductModal, setShowProductModal] = useState(false);
  const [newProductName, setNewProductName] = useState('');
  const [newProductType, setNewProductType] = useState('service');
  const [newSalesPrice, setNewSalesPrice] = useState('');
  const [newCostPrice, setNewCostPrice] = useState('');

  // Create Plan Form State
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [newPlanName, setNewPlanName] = useState('');
  const [newPlanPrice, setNewPlanPrice] = useState('');
  const [newBillingPeriod, setNewBillingPeriod] = useState('monthly');

  const fetchData = async () => {
    setLoading(true);
    setError('');
    const [pRes, plRes] = await Promise.all([getProducts(), getPlans()]);
    setLoading(false);

    if (pRes.success) setProducts(pRes.data || []);
    else setError(pRes.error || 'Failed to fetch products');

    if (plRes.success) {
      setPlans(plRes.data || []);
      if (pRes.data?.length > 0 && !selectedProductId) {
        setSelectedProductId(pRes.data[0].id);
      }
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    if (!newProductName.trim()) {
      const msg = 'Product name cannot be empty.';
      setError(msg);
      notify.error(msg);
      return;
    }
    const salesPriceNum = parseFloat(newSalesPrice);
    if (isNaN(salesPriceNum) || salesPriceNum < 0) {
      const msg = 'Sales price must be a non-negative number.';
      setError(msg);
      notify.error(msg);
      return;
    }

    const res = await createProduct({
      name: newProductName.trim(),
      product_type: newProductType,
      sales_price: salesPriceNum,
      cost_price: parseFloat(newCostPrice) || 0,
    });

    if (res.success) {
      const msg = `Product "${newProductName}" created successfully.`;
      setSuccess(msg);
      notify.success(msg);
      setShowProductModal(false);
      setNewProductName('');
      setNewSalesPrice('');
      setNewCostPrice('');
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to create product.';
      setError(errMsg);
      notify.error(errMsg);
    }
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    if (!newPlanName.trim()) {
      const msg = 'Plan name cannot be empty.';
      setError(msg);
      notify.error(msg);
      return;
    }
    const priceNum = parseFloat(newPlanPrice);
    if (isNaN(priceNum) || priceNum < 0) {
      const msg = 'Plan price must be a non-negative number.';
      setError(msg);
      notify.error(msg);
      return;
    }

    const res = await createPlan({
      product_id: parseInt(selectedProductId),
      name: newPlanName.trim(),
      price: priceNum,
      billing_period: newBillingPeriod,
    });

    if (res.success) {
      const msg = `Plan "${newPlanName}" created successfully.`;
      setSuccess(msg);
      notify.success(msg);
      setShowPlanModal(false);
      setNewPlanName('');
      setNewPlanPrice('');
      fetchData();
    } else {
      const errMsg = res.message || res.error || 'Failed to create plan.';
      setError(errMsg);
      notify.error(errMsg);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white tracking-tight">Products & Plans</h1>
          <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1">
            Configure catalog items, subscription pricing, and billing recurrence periods
          </p>
        </div>
        {user?.role === 'admin' && (
          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => setShowProductModal(true)}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-700 dark:text-slate-200 shadow-xs transition"
            >
              <Plus className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
              <span>Add Product</span>
            </button>
            <button
              onClick={() => setShowPlanModal(true)}
              className="flex-1 sm:flex-none flex items-center justify-center gap-1.5 px-3.5 py-2.5 min-h-[44px] text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition"
            >
              <Plus className="w-4 h-4" />
              <span>Add Plan</span>
            </button>
          </div>
        )}
      </div>

      <AlertBanner type="error" message={error} onClose={() => setError('')} />
      <AlertBanner type="success" message={success} onClose={() => setSuccess('')} />

      {/* Plans Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>Available Subscription Plans</span>
          </h2>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
            {plans.length} plan{plans.length === 1 ? '' : 's'} registered in PostgreSQL
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const product = products.find((p) => p.id === plan.product_id);
            return (
              <div
                key={plan.id}
                className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs flex flex-col justify-between hover:border-indigo-300 dark:hover:border-indigo-700 transition"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2.5 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-300 border border-indigo-100 dark:border-indigo-900 uppercase tracking-wide">
                      {plan.billing_period}
                    </span>
                    <span className="text-xs text-slate-400 dark:text-slate-500">ID #{plan.id}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900 dark:text-white truncate">{plan.name}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 truncate">
                    Product: <strong className="text-slate-700 dark:text-slate-300">{product?.name || `Product #${plan.product_id}`}</strong>
                  </p>
                </div>
                <div className="mt-5 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-baseline justify-between">
                  <div className="text-2xl font-extrabold text-slate-900 dark:text-white">
                    ₹{Number(plan.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                  <span className="text-xs text-slate-500 dark:text-slate-400 capitalize">per {plan.billing_period.replace('ly', '')}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Products Section */}
      <div className="space-y-4 pt-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
            <span>Base Catalog Products</span>
          </h2>
          <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">{products.length} catalog items</span>
        </div>

        {/* Structured Div Grid for md (>= 768px) and lg (>= 1280px) */}
        <div className="hidden md:block bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-xs overflow-hidden transition-colors">
          <div className="grid grid-cols-12 gap-4 px-5 py-3.5 bg-slate-50/70 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-xs font-semibold uppercase text-slate-500 dark:text-slate-400">
            <div className="col-span-1">ID</div>
            <div className="col-span-5">Product Name</div>
            <div className="col-span-2">Type</div>
            <div className="col-span-2 text-right">Standard Sales Price</div>
            <div className="col-span-2 text-right">Status</div>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-800">
            {products.map((p) => (
              <div key={p.id} className="grid grid-cols-12 gap-4 px-5 py-3.5 items-center hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition">
                <div className="col-span-1 font-mono text-xs text-slate-400 dark:text-slate-500">#{p.id}</div>
                <div className="col-span-5 font-semibold text-slate-900 dark:text-white truncate">{p.name}</div>
                <div className="col-span-2">
                  <span className="px-2.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-xs capitalize">
                    {p.product_type}
                  </span>
                </div>
                <div className="col-span-2 text-right font-medium text-slate-900 dark:text-white">
                  ₹{Number(p.sales_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </div>
                <div className="col-span-2 text-right">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-100 dark:border-emerald-900">
                    Active
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Card View below md (< 768px, phone base and sm) */}
        <div className="md:hidden space-y-3">
          {products.map((p) => (
            <div key={p.id} className="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-xs space-y-2.5 transition-colors">
              <div className="flex justify-between items-start gap-2">
                <div className="font-bold text-slate-900 dark:text-white break-words min-w-0">{p.name}</div>
                <span className="text-xs font-mono text-slate-400 dark:text-slate-500 shrink-0">#{p.id}</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-800">
                <span className="capitalize px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                  {p.product_type}
                </span>
                <span className="font-bold text-slate-900 dark:text-white text-base">
                  ₹{Number(p.sales_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Product Modal (Single column mobile, two column md+) */}
      {showProductModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-slate-200 dark:border-slate-800 my-auto">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Create New Product</h3>
            <form onSubmit={handleCreateProduct} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Product Name
                </label>
                <input
                  type="text"
                  required
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  placeholder="e.g. Cloud Storage Plus"
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Product Type
                  </label>
                  <select
                    value={newProductType}
                    onChange={(e) => setNewProductType(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  >
                    <option value="service">Service</option>
                    <option value="software">Software License</option>
                    <option value="addon">Add-on Feature</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Standard Sales Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={newSalesPrice}
                    onChange={(e) => setNewSalesPrice(e.target.value)}
                    placeholder="999.00"
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowProductModal(false)}
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Plan Modal (Single column mobile, two column md+) */}
      {showPlanModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white dark:bg-slate-900 rounded-2xl max-w-lg w-full p-5 sm:p-6 shadow-2xl border border-slate-200 dark:border-slate-800 my-auto">
            <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Create Subscription Plan</h3>
            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Linked Product
                </label>
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} (₹{Number(p.sales_price).toLocaleString('en-IN')})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                  Plan Display Name
                </label>
                <input
                  type="text"
                  required
                  value={newPlanName}
                  onChange={(e) => setNewPlanName(e.target.value)}
                  placeholder="e.g. Business Pro Annual"
                  className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Plan Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={newPlanPrice}
                    onChange={(e) => setNewPlanPrice(e.target.value)}
                    placeholder="1200.00"
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase mb-1.5">
                    Billing Period
                  </label>
                  <select
                    value={newBillingPeriod}
                    onChange={(e) => setNewBillingPeriod(e.target.value)}
                    className="w-full px-3.5 py-2.5 min-h-[44px] text-sm bg-slate-50/50 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white font-medium"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>

              <div className="flex flex-col-reverse sm:flex-row justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowPlanModal(false)}
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="w-full sm:w-auto px-4 py-2.5 min-h-[44px] text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm transition"
                >
                  Save Plan
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
