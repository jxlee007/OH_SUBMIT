import React from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

export default function AlertBanner({ type = 'error', message, onClose }) {
  if (!message) return null;

  const styles = {
    error: 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-900/70 text-rose-800 dark:text-rose-200',
    success: 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-900/70 text-emerald-800 dark:text-emerald-200',
    info: 'bg-sky-50 dark:bg-sky-950/60 border-sky-200 dark:border-sky-900/70 text-sky-800 dark:text-sky-200',
  };

  const icons = {
    error: <AlertCircle className="w-5 h-5 text-rose-500 dark:text-rose-400 shrink-0 mt-0.5" />,
    success: <CheckCircle2 className="w-5 h-5 text-emerald-500 dark:text-emerald-400 shrink-0 mt-0.5" />,
    info: <Info className="w-5 h-5 text-sky-500 dark:text-sky-400 shrink-0 mt-0.5" />,
  };

  return (
    <div className={`flex items-start gap-3 p-3.5 border rounded-xl shadow-xs transition duration-150 mb-4 ${styles[type] || styles.error}`}>
      {icons[type]}
      <div className="flex-1 text-sm font-medium leading-relaxed break-words min-w-0">
        {message}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="min-h-[44px] min-w-[44px] -my-2 -mr-2 flex items-center justify-center text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition"
          aria-label="Dismiss message"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
