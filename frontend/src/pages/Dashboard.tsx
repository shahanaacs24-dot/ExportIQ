import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Building2, Package, Globe, FileText, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import { profileApi } from '../api/profile';
import { productsApi } from '../api/products';
import api from '../api/client';
import type { MSMEProfile, Assessment } from '../types';
import Spinner from '../components/ui/Spinner';

export default function Dashboard() {
  const [profile, setProfile] = useState<MSMEProfile | null>(null);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [productsCount, setProductsCount] = useState(0);
  const [destsCount, setDestsCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [p, asList, prods, dests] = await Promise.all([
          profileApi.get().catch(() => null),
          api.get<Assessment[]>('/assessments').then(r => r.data).catch(() => []),
          productsApi.listProducts().catch(() => []),
          productsApi.listDestinations().catch(() => []),
        ]);
        setProfile(p);
        setAssessments(asList);
        setProductsCount(prods.length);
        setDestsCount(dests.length);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size="lg" message="Loading dashboard…" />
      </div>
    );
  }

  const completedCount = assessments.filter(a => a.status === 'completed').length;

  return (
    <div className="space-y-8">
      <div className="bg-gradient-to-r from-brand-600 to-brand-800 rounded-2xl p-8 text-white shadow-sm">
        <div className="max-w-3xl">
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome to ExportIQ{profile ? `, ${profile.business_name}` : ''}!
          </h1>
          <p className="mt-2 text-brand-100 text-sm leading-relaxed">
            Assess your MSME export readiness for international markets. Evaluate requirements, upload compliance documents, and calculate your Export Readiness Index (ERI).
          </p>
          <div className="mt-6 flex flex-wrap gap-4">
            {!profile ? (
              <Link
                to="/profile"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-brand-700 text-sm font-semibold rounded-xl hover:bg-brand-50 transition-colors shadow-sm"
              >
                <Building2 className="w-4 h-4" />
                Complete MSME Profile
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <Link
                to="/assessments"
                className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-brand-700 text-sm font-semibold rounded-xl hover:bg-brand-50 transition-colors shadow-sm"
              >
                <FileText className="w-4 h-4" />
                Start New Assessment
                <ArrowRight className="w-4 h-4" />
              </Link>
            )}
            <Link
              to="/products"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-brand-700/60 border border-brand-500 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 transition-colors"
            >
              <Package className="w-4 h-4" />
              Browse Products ({productsCount})
            </Link>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="MSME Profile"
          value={profile ? 'Configured' : 'Incomplete'}
          subtitle={profile ? profile.business_name : 'Action required'}
          icon={<Building2 className="w-6 h-6 text-brand-600" />}
          actionLink="/profile"
          actionText={profile ? 'View Profile' : 'Set up →'}
          status={profile ? 'success' : 'warning'}
        />
        <StatCard
          title="Supported Products"
          value={productsCount.toString()}
          subtitle="Ready for export check"
          icon={<Package className="w-6 h-6 text-brand-600" />}
          actionLink="/products"
          actionText="Browse →"
        />
        <StatCard
          title="Destination Countries"
          value={destsCount.toString()}
          subtitle="Global markets covered"
          icon={<Globe className="w-6 h-6 text-brand-600" />}
          actionLink="/products"
          actionText="View markets →"
        />
        <StatCard
          title="Assessments Run"
          value={assessments.length.toString()}
          subtitle={`${completedCount} completed`}
          icon={<FileText className="w-6 h-6 text-brand-600" />}
          actionLink="/assessments"
          actionText="View history →"
        />
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-gray-900">Recent Assessment</h2>
          <Link to="/assessments" className="text-sm text-brand-600 hover:text-brand-700 font-medium">
            View all ({assessments.length})
          </Link>
        </div>

        {assessments.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <FileText className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">No assessments yet</p>
            <p className="text-xs text-gray-500 mt-1">Start your first export readiness check to see results here.</p>
            <Link
              to="/assessments"
              className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
            >
              Start Assessment
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {assessments.slice(0, 3).map(a => (
              <div key={a.id} className="py-4 flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-gray-900">Assessment #{a.id}</span>
                    <span className={`text-xs px-2.5 py-0.5 rounded-full font-medium ${
                      a.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {a.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Created {new Date(a.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="text-right">
                  {a.eri_score !== null && a.eri_score !== undefined ? (
                    <div>
                      <span className="text-xl font-bold text-brand-600">{a.eri_score.toFixed(1)}</span>
                      <span className="text-xs text-gray-400"> / 100 ERI</span>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">Score pending</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, subtitle, icon, actionLink, actionText, status }: {
  title: string; value: string; subtitle: string; icon: React.ReactNode; actionLink: string; actionText: string; status?: 'success' | 'warning'
}) {
  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="bg-brand-50 p-3 rounded-xl">{icon}</div>
          {status === 'success' && <CheckCircle2 className="w-5 h-5 text-green-500" />}
          {status === 'warning' && <AlertCircle className="w-5 h-5 text-amber-500" />}
        </div>
        <h3 className="text-xs font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>
      </div>
      <div className="mt-4 pt-3 border-t border-gray-100">
        <Link to={actionLink} className="text-xs font-semibold text-brand-600 hover:text-brand-700 inline-flex items-center gap-1">
          {actionText}
        </Link>
      </div>
    </div>
  );
}
