import { useState, useEffect } from 'react';

export function getStoredTheme() {
  if (typeof window === 'undefined') return 'light';
  try {
    const stored = localStorage.getItem('bl_theme');
    if (stored === 'dark' || stored === 'light') return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  } catch (e) {
    return 'light';
  }
}

export function applyTheme(theme) {
  if (typeof document === 'undefined') return;
  const isDark = theme === 'dark';
  document.documentElement.classList.toggle('dark', isDark);
  try {
    localStorage.setItem('bl_theme', theme);
  } catch (e) {}
}

export function useTheme() {
  const [theme, setThemeState] = useState(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  const toggleTheme = () => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  return { theme, isDark: theme === 'dark', toggleTheme, setTheme: setThemeState };
}

