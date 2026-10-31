import { toast } from 'react-toastify';

/**
 * Toast Notification Service
 * Enforces accessibility roles and dismissal timeouts across light and dark themes.
 * Pages must call these helpers, never toast() directly.
 */
export const notify = {
  success: (message, options = {}) => {
    return toast.success(message, {
      autoClose: 4000,
      role: 'status',
      ...options,
    });
  },

  error: (message, options = {}) => {
    return toast.error(message, {
      autoClose: 6000,
      pauseOnHover: true,
      role: 'alert',
      ...options,
    });
  },

  info: (message, options = {}) => {
    return toast.info(message, {
      autoClose: 4000,
      role: 'status',
      ...options,
    });
  },

  warning: (message, options = {}) => {
    return toast.warning(message, {
      autoClose: 5000,
      role: 'status',
      ...options,
    });
  },

  /**
   * Automatically maps API response envelope to appropriate toast:
   * - Success envelope -> success toast with short message (custom or server message)
   * - Error envelope (400, 409, 422, etc.) -> error toast displaying server message as-is
   */
  fromApiResponse: (res, defaultSuccessMsg = 'Operation completed successfully.') => {
    if (!res) return false;
    if (res.success) {
      const msg = res.message || defaultSuccessMsg;
      notify.success(msg);
      return true;
    } else {
      // 409 Conflict, 422 Unprocessable Entity, 400 Bad Request, etc.
      const msg = res.message || res.error || 'Operation failed.';
      notify.error(msg);
      return false;
    }
  },
};

export const success = notify.success;
export const error = notify.error;
export const info = notify.info;
export const warning = notify.warning;
export const fromApiResponse = notify.fromApiResponse;

export default notify;

