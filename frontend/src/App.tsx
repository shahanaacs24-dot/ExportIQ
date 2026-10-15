import { Routes, Route, Navigate, Link, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { Building2, Package, FileText, BarChart3, LogOut, ShieldCheck, Upload } from 'lucide-react';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProfilePage from './pages/ProfilePage';
import ProductsPage from './pages/ProductsPage';
import AssessmentsPage from './pages/AssessmentsPage';
import DocumentsPage from './pages/DocumentsPage';

function ProtectedLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-brand-600 text-white p-2 rounded-lg font-bold text-xl flex items-center shadow-sm">
              <ShieldCheck className="w-6 h-6 mr-1.5" />
              ExportIQ
            </div>
            <span className="text-xs bg-brand-50 text-brand-700 font-medium px-2.5 py-1 rounded-full border border-brand-100 hidden sm:inline">
              MSME Export Readiness Platform
            </span>
          </div>

          <nav className="hidden md:flex items-center space-x-1">
            <NavLink to="/" icon={<BarChart3 className="w-4 h-4 mr-1.5" />} label="Dashboard" />
            <NavLink to="/profile" icon={<Building2 className="w-4 h-4 mr-1.5" />} label="MSME Profile" />
            <NavLink to="/documents" icon={<Upload className="w-4 h-4 mr-1.5" />} label="Documents" />
            <NavLink to="/products" icon={<Package className="w-4 h-4 mr-1.5" />} label="Products & Destinations" />
            <NavLink to="/assessments" icon={<FileText className="w-4 h-4 mr-1.5" />} label="Assessments" />
          </nav>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleLogout}
              className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-red-600 px-3 py-1.5 rounded-md hover:bg-gray-100 transition-colors"
              title="Logout"
            >
              <LogOut className="w-4 h-4 mr-1.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </header>

      <div className="md:hidden bg-white border-b border-gray-200 px-4 py-2 flex space-x-2 overflow-x-auto">
        <MobileNavLink to="/" label="Dashboard" />
        <MobileNavLink to="/profile" label="Profile" />
        <MobileNavLink to="/documents" label="Documents" />
        <MobileNavLink to="/products" label="Products" />
        <MobileNavLink to="/assessments" label="Assessments" />
      </div>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/assessments" element={<AssessmentsPage />} />
        </Routes>
      </main>

      <footer className="bg-white border-t border-gray-200 py-4 text-center text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
          <p>© 2026 ExportIQ. Academic decision-support tool for Indian MSMEs.</p>
          <p className="text-gray-400">Disclaimer: Indicative assessment only. Not official certification.</p>
        </div>
      </footer>
    </div>
  );
}

function NavLink({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link
      to={to}
      className={`inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        active
          ? 'bg-brand-50 text-brand-700 font-semibold'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
      }`}
    >
      {icon}
      {label}
    </Link>
  );
}

function MobileNavLink({ to, label }: { to: string; label: string }) {
  const location = useLocation();
  const active = location.pathname === to;
  return (
    <Link
      to={to}
      className={`px-3 py-1.5 rounded-md text-xs font-medium whitespace-nowrap ${
        active ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-700'
      }`}
    >
      {label}
    </Link>
  );
}

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/*" element={<ProtectedLayout />} />
      </Routes>
    </>
  );
}
