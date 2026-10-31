/**
 * Centralized API client service.
 * Handles pure in-memory JWT access token storage, httpOnly cookie session hydration,
 * standardized response envelope unwrapping, and 3-layer validation error formatting.
 * 
 * ZERO tokens or user objects stored in localStorage or sessionStorage.
 */

const BASE_URL = '';

// Pure runtime in-memory state — completely purged on browser tab close/hard navigation
let inMemoryAccessToken = null;
let currentUser = null;

export function setAuthToken(token, user = null) {
  inMemoryAccessToken = token;
  if (user) {
    currentUser = user;
  }
}

export function getAuthToken() {
  return inMemoryAccessToken;
}

export function getCurrentUser() {
  return currentUser;
}

export function clearAuth() {
  inMemoryAccessToken = null;
  currentUser = null;
}

/**
 * Standard HTTP request wrapper with credentials & Bearer auth injection
 */
export async function apiRequest(endpoint, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    ...options.headers,
  };

  if (inMemoryAccessToken) {
    headers['Authorization'] = `Bearer ${inMemoryAccessToken}`;
  }

  const config = {
    ...options,
    headers,
    credentials: 'include', // Automatically passes httpOnly cookies across requests
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    const result = await response.json().catch(() => null);

    if (!response.ok) {
      const errorMessage =
        result?.message ||
        result?.detail ||
        result?.error ||
        `Request failed with status ${response.status}`;
      return {
        success: false,
        data: null,
        error: errorMessage,
        message: errorMessage,
        status: response.status,
      };
    }

    return {
      success: result?.success ?? true,
      data: result?.data ?? result,
      error: result?.error ?? null,
      message: result?.message ?? null,
      status: response.status,
    };
  } catch (err) {
    return {
      success: false,
      data: null,
      error: 'Network connection failed. Please ensure the backend server is running locally.',
      message: err.message,
      status: 0,
    };
  }
}

// ── Health ──────────────────────────────────────────────────────────────────
export async function getHealthStatus() {
  return await apiRequest('/api/health');
}

// ── Auth & Session Hydration ────────────────────────────────────────────────
export async function loginUser(email, password) {
  const res = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (res.success && res.data?.access_token) {
    setAuthToken(res.data.access_token, res.data.user);
  }
  return res;
}

export async function registerUser(payload) {
  return await apiRequest('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Hydrates in-memory access token on page reload via httpOnly refresh cookie.
 * Does not read or write to Web Storage.
 */
export async function restoreSession() {
  const res = await apiRequest('/api/auth/refresh', {
    method: 'POST',
  });
  if (res.success && res.data?.access_token) {
    setAuthToken(res.data.access_token, res.data.user);
    return res.data.user;
  }
  clearAuth();
  return null;
}

export async function logoutUser() {
  await apiRequest('/api/auth/logout', { method: 'POST' });
  clearAuth();
}

// ── Dashboard (Read-Only Aggregate View) ────────────────────────────────────
export async function getDashboardSummary() {
  return await apiRequest('/api/dashboard/summary');
}

// ── Products & Plans ────────────────────────────────────────────────────────
export async function getProducts() {
  return await apiRequest('/api/products');
}

export async function createProduct(payload) {
  return await apiRequest('/api/products', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getPlans() {
  return await apiRequest('/api/plans');
}

export async function createPlan(payload) {
  return await apiRequest('/api/plans', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ── Subscriptions ───────────────────────────────────────────────────────────
export async function getSubscriptions(status = '') {
  const query = status ? `?status=${encodeURIComponent(status)}` : '';
  return await apiRequest(`/api/subscriptions${query}`);
}

export async function createSubscription(payload) {
  return await apiRequest('/api/subscriptions', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateSubscriptionStatus(id, newStatus) {
  return await apiRequest(`/api/subscriptions/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status: newStatus }),
  });
}

// ── Invoices ────────────────────────────────────────────────────────────────
export async function getInvoices(overdueOnly = false, status = '') {
  const params = new URLSearchParams();
  if (overdueOnly) params.append('overdue_only', 'true');
  if (status) params.append('status', status);
  const query = params.toString() ? `?${params.toString()}` : '';
  return await apiRequest(`/api/invoices${query}`);
}

export async function generateInvoice(payload) {
  return await apiRequest('/api/invoices', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateInvoiceStatus(id, newStatus) {
  return await apiRequest(`/api/invoices/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status: newStatus }),
  });
}

// ── Payments ────────────────────────────────────────────────────────────────
export async function getPayments() {
  return await apiRequest('/api/payments');
}

export async function createPayment(payload) {
  return await apiRequest('/api/payments', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getOutstandingInvoices() {
  return await apiRequest('/api/payments/outstanding');
}
