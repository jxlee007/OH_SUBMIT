import React, { useEffect, useState } from 'react';
import { getProducts, createProduct, getPlans, createPlan, getCurrentUser } from '../services/api';
import AlertBanner from '../components/AlertBanner';
import { Package, Plus, Calendar, Tag, ShieldAlert } from 'lucide-react';

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
      setError('Product name cannot be empty.');
      return;
    }
    const salesPriceNum = parseFloat(newSalesPrice);
    if (isNaN(salesPriceNum) || salesPriceNum < 0) {
      setError('Sales price must be a non-negative number.');
      return;
    }

    const res = await createProduct({
      name: newProductName.trim(),
      product_type: newProductType,
      sales_price: salesPriceNum,
      cost_price: parseFloat(newCostPrice) || 0,
    });

    if (res.success) {
      setSuccess(`Product "${newProductName}" created successfully.`);
      setShowProductModal(false);
      setNewProductName('');
      setNewSalesPrice('');
      setNewCostPrice('');
      fetchData();
    } else {
      setError(res.error || 'Failed to create product.');
    }
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    if (!newPlanName.trim()) {
      setError('Plan name cannot be empty.');
      return;
    }
    const priceNum = parseFloat(newPlanPrice);
    if (isNaN(priceNum) || priceNum < 0) {
      setError('Plan price must be a non-negative number.');
      return;
    }

    const res = await createPlan({
      product_id: parseInt(selectedProductId),
      name: newPlanName.trim(),
      price: priceNum,
      billing_period: newBillingPeriod,
    });

    if (res.success) {
      setSuccess(`Plan "${newPlanName}" created successfully.`);
      setShowPlanModal(false);
      setNewPlanName('');
      setNewPlanPrice('');
      fetchData();
    } else {
      setError(res.error || 'Failed to create plan.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-6 border-b border-slate-200">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">Products & Plans</h1>
          <p className="text-sm text-slate-500 mt-1">
            Configure catalog items, subscription pricing, and billing recurrence periods
          </p>
        </div>
        {user?.role === 'admin' && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowProductModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium bg-white hover:bg-slate-50 border border-slate-200 rounded-lg text-slate-700 shadow-xs transition"
            >
              <Plus className="w-4 h-4 text-indigo-600" />
              <span>Add Product</span>
            </button>
            <button
              onClick={() => setShowPlanModal(true)}
              className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg shadow-sm transition"
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
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-indigo-600" />
            <span>Available Subscription Plans</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            {plans.length} plan{plans.length === 1 ? '' : 's'} registered in PostgreSQL
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plans.map((plan) => {
            const product = products.find((p) => p.id === plan.product_id);
            return (
              <div
                key={plan.id}
                className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col justify-between hover:border-indigo-200 transition"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 border border-indigo-100 uppercase tracking-wide">
                      {plan.billing_period}
                    </span>
                    <span className="text-xs text-slate-400">ID #{plan.id}</span>
                  </div>
                  <h3 className="text-base font-bold text-slate-900">{plan.name}</h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Product: <strong className="text-slate-700">{product?.name || `Product #${plan.product_id}`}</strong>
                  </p>
                </div>
                <div className="mt-5 pt-4 border-t border-slate-100 flex items-baseline justify-between">
                  <div className="text-2xl font-extrabold text-slate-900">
                    ₹{Number(plan.price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                  <span className="text-xs text-slate-500 capitalize">per {plan.billing_period.replace('ly', '')}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Products Section */}
      <div className="space-y-4 pt-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-600" />
            <span>Base Catalog Products</span>
          </h2>
          <span className="text-xs text-slate-500 font-medium">{products.length} catalog items</span>
        </div>

        {/* Responsive Table for 768px/1280px and Cards for 375px */}
        <div className="hidden sm:block bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50/70 border-b border-slate-200 text-xs font-semibold uppercase text-slate-500">
              <tr>
                <th className="px-5 py-3.5">ID</th>
                <th className="px-5 py-3.5">Product Name</th>
                <th className="px-5 py-3.5">Type</th>
                <th className="px-5 py-3.5 text-right">Standard Sales Price</th>
                <th className="px-5 py-3.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/50 transition">
                  <td className="px-5 py-3.5 font-mono text-xs text-slate-400">#{p.id}</td>
                  <td className="px-5 py-3.5 font-semibold text-slate-900">{p.name}</td>
                  <td className="px-5 py-3.5 capitalize text-xs">
                    <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium">
                      {p.product_type}
                    </span>
                  </td>
                  <td className="px-5 py-3.5 text-right font-medium text-slate-900">
                    ₹{Number(p.sales_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700">
                      Active
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* 375px Mobile View */}
        <div className="sm:hidden space-y-3">
          {products.map((p) => (
            <div key={p.id} className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs space-y-2">
              <div className="flex justify-between items-start">
                <div className="font-bold text-slate-900">{p.name}</div>
                <span className="text-xs font-mono text-slate-400">#{p.id}</span>
              </div>
              <div className="flex justify-between items-center text-xs text-slate-500 pt-2 border-t border-slate-100">
                <span className="capitalize">{p.product_type}</span>
                <span className="font-bold text-slate-900 text-sm">
                  ₹{Number(p.sales_price).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Add Product Modal */}
      {showProductModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Create New Product</h3>
            <form onSubmit={handleCreateProduct} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Product Name</label>
                <input
                  type="text"
                  required
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  placeholder="e.g. Cloud Storage Plus"
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Product Type</label>
                <select
                  value={newProductType}
                  onChange={(e) => setNewProductType(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                >
                  <option value="service">Service</option>
                  <option value="software">Software License</option>
                  <option value="addon">Add-on Feature</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Standard Sales Price (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={newSalesPrice}
                  onChange={(e) => setNewSalesPrice(e.target.value)}
                  placeholder="999.00"
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500/20"
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowProductModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
                >
                  Save Product
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Add Plan Modal */}
      {showPlanModal && (
        <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-slate-100">
            <h3 className="text-lg font-bold text-slate-900 mb-4">Create Subscription Plan</h3>
            <form onSubmit={handleCreatePlan} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Linked Product</label>
                <select
                  value={selectedProductId}
                  onChange={(e) => setSelectedProductId(e.target.value)}
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                >
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} (₹{Number(p.sales_price).toLocaleString('en-IN')})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Plan Display Name</label>
                <input
                  type="text"
                  required
                  value={newPlanName}
                  onChange={(e) => setNewPlanName(e.target.value)}
                  placeholder="e.g. Business Pro Annual"
                  className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Plan Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={newPlanPrice}
                    onChange={(e) => setNewPlanPrice(e.target.value)}
                    placeholder="1200.00"
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Billing Period</label>
                  <select
                    value={newBillingPeriod}
                    onChange={(e) => setNewBillingPeriod(e.target.value)}
                    className="w-full px-3 py-2 text-sm border border-slate-300 rounded-lg font-medium"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowPlanModal(false)}
                  className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
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
