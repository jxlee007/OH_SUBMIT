import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUser, clearAuth, getAuthToken, logoutUser } from '../services/api';
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
  ShieldCheck
} from 'lucide-react';

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const user = getCurrentUser();
  const token = getAuthToken();
  const isAuthenticated = Boolean(token || user);

  const handleLogout = async () => {
    await logoutUser();
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
    <header className="sticky top-0 z-40 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2 group">
              <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-sm group-hover:bg-indigo-700 transition">
                B
              </div>
              <div>
                <span className="font-bold text-slate-900 tracking-tight text-lg">Brightloop</span>
                <span className="text-xs ml-1.5 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 font-medium border border-slate-200">
                  Subscriptions
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Navigation (>= 768px tablet, >= 1280px desktop) */}
          <nav className="hidden md:flex items-center gap-1">
            {isAuthenticated &&
              visibleLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition ${
                      isActive
                        ? 'bg-indigo-50 text-indigo-700 font-semibold'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
          </nav>

          {/* User Session & Actions */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated && user ? (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-xs font-semibold text-slate-900">{user.full_name || user.email}</div>
                  <div className="inline-flex items-center gap-1 text-[11px] font-medium text-indigo-600 uppercase tracking-wide">
                    <ShieldCheck className="w-3 h-3 inline" />
                    {user.role}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-slate-500 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
                  title="Logout"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-700 hover:text-indigo-600 hover:bg-slate-50 rounded-lg transition"
                >
                  <LogIn className="w-4 h-4" />
                  <span>Login</span>
                </Link>
                <Link
                  to="/register"
                  className="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg transition shadow-sm"
                >
                  <UserPlus className="w-4 h-4" />
                  <span>Register</span>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button (375px) */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer (375px breakpoint optimization) */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {isAuthenticated ? (
            <>
              <div className="py-2 border-b border-slate-100 mb-2">
                <div className="text-sm font-semibold text-slate-800">{user?.full_name || user?.email}</div>
                <div className="text-xs text-indigo-600 uppercase font-bold">{user?.role}</div>
              </div>
              {visibleLinks.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.path;
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium ${
                      isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-700 hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              <button
                onClick={handleLogout}
                className="w-full mt-3 flex items-center gap-3 px-3 py-2 text-sm font-medium text-rose-600 hover:bg-rose-50 rounded-lg"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <div className="pt-2 flex flex-col gap-2">
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-slate-700 border border-slate-300 rounded-lg"
              >
                <LogIn className="w-4 h-4" /> Login
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg"
              >
                <UserPlus className="w-4 h-4" /> Register
              </Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
