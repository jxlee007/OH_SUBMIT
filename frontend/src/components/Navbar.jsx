import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUser, getAuthToken, logoutUser } from '../services/api';
import { useTheme } from '../utils/theme';
import { 
  LayoutDashboard, 
  Package, 
  Repeat, 
  Receipt, 
  CreditCard, 
  LogOut, 
  LogIn, 
  UserPlus, 
  Menu, 
  X,
  ShieldCheck,
  Sun,
  Moon
} from 'lucide-react';

export default function Navbar({ user: propUser, onLogout: propOnLogout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const user = propUser !== undefined ? propUser : getCurrentUser();
  const token = getAuthToken();
  const isAuthenticated = Boolean(user || token);
  const { isDark, toggleTheme } = useTheme();

  // Close drawer on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  // Close drawer on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && mobileMenuOpen) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [mobileMenuOpen]);

  // Prevent background scroll when mobile drawer is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [mobileMenuOpen]);

  const handleLogout = async () => {
    await logoutUser();
    if (propOnLogout) propOnLogout();
    setMobileMenuOpen(false);
    navigate('/login');
  };

  const navLinks = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard, roles: ['admin', 'staff', 'customer'] },
    { name: 'Products & Plans', path: '/products', icon: Package, roles: ['admin', 'staff'] },
    { name: 'Subscriptions', path: '/subscriptions', icon: Repeat, roles: ['admin', 'staff', 'customer'] },
    { name: 'Invoices', path: '/invoices', icon: Receipt, roles: ['admin', 'staff', 'customer'] },
    { name: 'Payments', path: '/payments', icon: CreditCard, roles: ['admin', 'staff'] },
  ];

  const visibleLinks = navLinks.filter(
    (item) => !user || item.roles.includes(user.role || 'customer')
  );

  return (
    <header className="sticky top-0 z-40 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-xs transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2 group min-h-[44px]">
              <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-xs group-hover:bg-indigo-700 transition">
                B
              </div>
              <div className="flex items-baseline">
                <span className="font-bold text-slate-900 dark:text-white tracking-tight text-lg">Brightloop</span>
                <span className="text-xs ml-1.5 px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium border border-slate-200 dark:border-slate-700 hidden sm:inline">
                  Subscriptions
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation (md: >= 768px, lg: >= 1280px) */}
          <nav className="hidden md:flex items-center gap-1">
            {isAuthenticated &&
              visibleLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition min-h-[44px] ${
                      isActive
                        ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-700 dark:text-indigo-400 font-semibold'
                        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
          </nav>

          {/* Desktop Actions & Theme Toggle */}
          <div className="hidden md:flex items-center gap-3">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              aria-label="Toggle theme"
            >
              {isDark ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600" />}
            </button>

            {isAuthenticated && user ? (
              <div className="flex items-center gap-3 pl-2 border-l border-slate-200 dark:border-slate-700">
                <div className="text-right">
                  <div className="text-xs font-semibold text-slate-900 dark:text-slate-100 truncate max-w-[140px]">
                    {user.full_name || user.email}
                  </div>
                  <div className="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-600 dark:text-indigo-400 uppercase tracking-wide">
                    <ShieldCheck className="w-3 h-3 inline" />
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="min-h-[44px] min-w-[44px] flex items-center justify-center text-slate-500 dark:text-slate-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 rounded-lg transition"
                  title="Logout"
                  aria-label="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="flex items-center gap-1.5 px-3 py-2 text-sm font-medium text-slate-700 dark:text-slate-200 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition min-h-[44px]"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Login</span>
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition shadow-xs min-h-[44px]"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Right Controls (< 768px): Theme Toggle + Hamburger Drawer Trigger */}
          <div className="md:hidden flex items-center gap-1">
            <button
              onClick={toggleTheme}
              className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              title={isDark ? "Light mode" : "Dark mode"}
              aria-label="Toggle color theme"
            >
              {isDark ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-slate-600 dark:text-slate-300" />}
            </button>
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              aria-label="Open navigation drawer"
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Full-Height Mobile Drawer (< 768px) with Backdrop Blur */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden flex justify-end" role="dialog" aria-modal="true">
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-slate-950/60 backdrop-blur-xs transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
            aria-hidden="true"
          />

          {/* Slide-out Drawer Panel */}
          <div className="relative w-full max-w-xs bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col justify-between z-10 border-l border-slate-200 dark:border-slate-800 overflow-y-auto">
            {/* Drawer Header */}
            <div>
              <div className="flex items-center justify-between p-4 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">
                    B
                  </div>
                  <span className="font-bold text-slate-900 dark:text-white text-base">Brightloop</span>
                </div>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                  aria-label="Close navigation drawer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* User Identity Banner (if logged in) */}
              {isAuthenticated && user && (
                <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800">
                  <div className="text-sm font-semibold text-slate-900 dark:text-slate-100 truncate">
                    {user.full_name || user.email}
                  </div>
                  <div className="inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 font-bold uppercase mt-0.5 tracking-wider">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    <span>{user.role}</span>
                  </div>
                </div>
              )}

              {/* Navigation Links */}
              <nav className="p-4 space-y-1.5">
                {isAuthenticated ? (
                  visibleLinks.map((item) => {
                    const Icon = item.icon;
                    const isActive = location.pathname === item.path;
                    return (
                      <Link
                        key={item.path}
                        to={item.path}
                        onClick={() => setMobileMenuOpen(false)}
                        className={`flex items-center gap-3 px-3.5 py-3 rounded-xl text-base font-medium min-h-[44px] transition ${
                          isActive
                            ? 'bg-indigo-50 dark:bg-indigo-950/70 text-indigo-700 dark:text-indigo-400 font-bold'
                            : 'text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800'
                        }`}
                      >
                        <Icon className="w-5 h-5 shrink-0" />
                        <span>{item.name}</span>
                      </Link>
                    );
                  })
                ) : (
                  <div className="space-y-2 pt-2">
                    <Link
                      to="/login"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl text-base font-semibold text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800 min-h-[44px] transition"
                    >
                      <LogIn className="w-5 h-5" />
                      <span>Sign In</span>
                    </Link>
                    <Link
                      to="/register"
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl text-base font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm min-h-[44px] transition"
                    >
                      <UserPlus className="w-5 h-5" />
                      <span>Register Account</span>
                    </Link>
                  </div>
                )}
              </nav>
            </div>

            {/* Drawer Footer Actions */}
            <div className="p-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
              {/* Theme Toggle inside Drawer */}
              <div className="flex items-center justify-between p-2 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 pl-2">Theme Mode</span>
                <button
                  onClick={toggleTheme}
                  className="min-h-[44px] px-3 flex items-center gap-2 text-xs font-semibold rounded-lg bg-white dark:bg-slate-700 text-slate-800 dark:text-slate-100 shadow-xs border border-slate-200 dark:border-slate-600"
                >
                  {isDark ? (
                    <>
                      <Sun className="w-4 h-4 text-amber-400" />
                      <span>Dark</span>
                    </>
                  ) : (
                    <>
                      <Moon className="w-4 h-4 text-indigo-600" />
                      <span>Light</span>
                    </>
                  )}
                </button>
              </div>

              {isAuthenticated && (
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-semibold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 hover:bg-rose-100 dark:hover:bg-rose-950/60 min-h-[44px] transition"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout from Session</span>
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
