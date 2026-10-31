/**
 * Centralized API client service.
 * Handles standardized response unwrapping and friendly error messaging.
 */

const BASE_URL = '';

/**
 * Standard HTTP request wrapper
 * @param {string} endpoint 
 * @param {RequestInit} options 
 * @returns {Promise<{success: boolean, data: any, error: string | null, message: string | null}>}
 */
export async function apiRequest(endpoint, options = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    const result = await response.json().catch(() => null);

    if (!response.ok) {
      // 400, 422, 500 error payload handling
      const errorMessage = result?.message || result?.error || `Request failed with status ${response.status}`;
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
    // Network or offline failure
    return {
      success: false,
      data: null,
      error: 'Network connection failed. Please ensure the backend is running locally.',
      message: err.message,
      status: 0,
    };
  }
}

/**
 * Fetches system & database health from backend
 */
export async function getHealthStatus() {
  return await apiRequest('/api/health');
}

