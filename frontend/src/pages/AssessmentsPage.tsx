import React, { useEffect, useState } from 'react';
import { FileText, Plus, Download, ChevronRight, ArrowLeft } from 'lucide-react';
import api from '../api/client';
import { productsApi } from '../api/products';
import type { Assessment, Product, DestinationCountry } from '../types';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';
import toast from 'react-hot-toast';

export default function AssessmentsPage() {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [selectedAssessment, setSelectedAssessment] = useState<any | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [destinations, setDestinations] = useState<DestinationCountry[]>([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);

  const [selectedProduct, setSelectedProduct] = useState<number>(0);
  const [selectedDest, setSelectedDest] = useState<number>(0);
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      const [asList, prods, dests] = await Promise.all([
        api.get<Assessment[]>('/assessments').then(r => r.data),
        productsApi.listProducts(),
        productsApi.listDestinations(),
      ]);
      setAssessments(asList);
      setProducts(prods);
      setDestinations(dests);
      if (prods.length > 0) setSelectedProduct(prods[0].id);
      if (dests.length > 0) setSelectedDest(dests[0].id);
    } catch {
      setError('Failed to load assessments.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const openDetail = async (id: number) => {
    setDetailLoading(true);
    try {
      const { data } = await api.get<any>(`/assessments/${id}`);
      setSelectedAssessment(data);
    } catch {
      toast.error('Failed to load assessment details.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProduct || !selectedDest) {
      toast.error('Please select both a product and a destination country.');
      return;
    }
    setSubmitting(true);
    try {
      const { data } = await api.post<Assessment>('/assessments', {
        product_id: Number(selectedProduct),
        destination_country_id: Number(selectedDest),
      });
      const submitted = await api.post<Assessment>(`/assessments/${data.id}/submit`);
      setAssessments(prev => [submitted.data, ...prev]);
      setShowModal(false);
      toast.success('Assessment evaluated successfully!');
      openDetail(submitted.data.id);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create assessment');
    } finally {
      setSubmitting(false);
    }
  };

  const downloadPdf = async (id: number) => {
    try {
      const response = await api.get(`/reports/${id}/pdf`, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ExportIQ_Report_Assessment_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('PDF report downloaded successfully!');
    } catch {
      toast.error('Failed to download PDF report.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size="lg" message="Loading assessments…" />
      </div>
    );
  }

  if (selectedAssessment) {
    const breakdown = selectedAssessment.score_breakdown || {};
    const recommendations = breakdown.recommendations || [];
    const catScores = selectedAssessment.category_scores || {};

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setSelectedAssessment(null)}
            className="inline-flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-gray-900"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Assessments
          </button>
          <button
            onClick={() => downloadPdf(selectedAssessment.id)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" /> Download PDF Report
          </button>
        </div>

        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold text-gray-900">Assessment #{selectedAssessment.id}</h1>
              <span className="text-xs px-2.5 py-1 rounded-full font-medium bg-green-100 text-green-700 uppercase">
                {selectedAssessment.status}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Evaluated on {selectedAssessment.submitted_at ? new Date(selectedAssessment.submitted_at).toLocaleString() : '—'}
            </p>
          </div>
          <div className="text-right bg-brand-50 border border-brand-100 px-5 py-3 rounded-xl">
            <div className="text-3xl font-bold text-brand-600">
              {selectedAssessment.eri_score !== null && selectedAssessment.eri_score !== undefined
                ? selectedAssessment.eri_score.toFixed(1)
                : '—'}
            </div>
            <div className="text-xs font-medium text-brand-700">Export Readiness Index (0-100)</div>
          </div>
        </div>

        {Object.keys(catScores).length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Category Breakdown</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Object.entries(catScores).map(([cat, score]) => (
                <div key={cat} className="bg-gray-50 border border-gray-100 rounded-xl p-4">
                  <p className="text-xs font-medium text-gray-500 capitalize">{cat.replace('_', ' ')}</p>
                  <p className="text-xl font-bold text-gray-900 mt-1">{String(score)}%</p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Requirements Compliance Results</h2>
          <div className="divide-y divide-gray-100">
            {selectedAssessment.requirement_results.map((r: any) => (
              <div key={r.id} className="py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-900">{r.requirement?.name}</span>
                    <span className="text-xs text-gray-400">({r.requirement?.code})</span>
                  </div>
                  <p className="text-xs text-gray-600">{r.explanation}</p>
                  {r.requirement?.source_url && (
                    <a href={r.requirement.source_url} target="_blank" rel="noreferrer" className="text-xs text-brand-600 hover:underline inline-block">
                      Source: {r.requirement.issuing_authority || 'Official Portal'} ↗
                    </a>
                  )}
                </div>
                <StatusBadge status={r.status} />
              </div>
            ))}
          </div>
        </div>

        {recommendations.length > 0 && (
          <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Prioritized Recommendations & Next Steps</h2>
            <div className="space-y-3">
              {recommendations.map((rec: any, idx: number) => (
                <div key={idx} className="bg-amber-50/60 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
                  <div className="bg-amber-600 text-white font-bold text-xs px-2 py-1 rounded">
                    P{rec.priority}
                  </div>
                  <div className="flex-1 text-sm">
                    <p className="font-semibold text-gray-900">{rec.title}</p>
                    <p className="text-gray-700 mt-0.5">{rec.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Assessments</h1>
          <p className="text-sm text-gray-500 mt-1">
            Run export readiness evaluations and review compliance scores and gap analysis.
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 transition-colors shadow-sm"
        >
          <Plus className="w-4 h-4" />
          New Assessment
        </button>
      </div>

      {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

      {detailLoading && (
        <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm flex items-center justify-center">
          <Spinner size="lg" message="Loading assessment details…" />
        </div>
      )}

      {assessments.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center shadow-sm">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h2 className="text-base font-semibold text-gray-800">No assessments recorded yet</h2>
          <p className="text-sm text-gray-500 mt-1 max-w-md mx-auto">
            Create your first readiness assessment by selecting an export product and a destination country.
          </p>
          <button
            onClick={() => setShowModal(true)}
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-xl hover:bg-brand-700 transition-colors"
          >
            <Plus className="w-4 h-4" /> Start Assessment
          </button>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden">
          <div className="divide-y divide-gray-200">
            {assessments.map(a => (
              <div key={a.id} className="p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-gray-50/50 transition-colors">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="font-semibold text-gray-900">Assessment #{a.id}</span>
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                      a.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {a.status.toUpperCase()}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Created: {new Date(a.created_at).toLocaleString()}
                    {a.submitted_at && ` · Evaluated: ${new Date(a.submitted_at).toLocaleDateString()}`}
                  </p>
                </div>

                <div className="flex items-center gap-6">
                  {a.eri_score !== null && a.eri_score !== undefined ? (
                    <div className="text-right">
                      <div className="text-2xl font-bold text-brand-600">{a.eri_score.toFixed(1)}</div>
                      <div className="text-xs text-gray-400">ERI Score / 100</div>
                    </div>
                  ) : (
                    <span className="text-xs text-gray-400">Pending evaluation</span>
                  )}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => downloadPdf(a.id)}
                      className="p-2 border border-gray-200 text-gray-600 hover:text-brand-600 rounded-lg hover:bg-gray-50 transition-colors"
                      title="Download PDF Report"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => openDetail(a.id)}
                      className="inline-flex items-center gap-1 px-3 py-2 bg-brand-50 text-brand-700 hover:bg-brand-100 rounded-lg text-sm font-medium transition-colors"
                    >
                      View <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-200">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Start New Export Readiness Assessment</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select Product</label>
                <select
                  value={selectedProduct}
                  onChange={e => setSelectedProduct(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
                >
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.name} (HS: {p.hs_code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Select Destination Country</label>
                <select
                  value={selectedDest}
                  onChange={e => setSelectedDest(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white"
                >
                  {destinations.map(d => (
                    <option key={d.id} value={d.id}>{d.name} ({d.iso_code})</option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center gap-2 px-5 py-2 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:bg-brand-300"
                >
                  {submitting && <Spinner size="sm" />}
                  {submitting ? 'Evaluating…' : 'Evaluate Readiness'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { bg: string; text: string; label: string }> = {
    compliant: { bg: 'bg-green-100', text: 'text-green-700', label: 'Compliant' },
    missing: { bg: 'bg-red-100', text: 'text-red-700', label: 'Missing' },
    incomplete: { bg: 'bg-amber-100', text: 'text-amber-700', label: 'Incomplete' },
    expired: { bg: 'bg-orange-100', text: 'text-orange-700', label: 'Expired' },
    unverified: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Unverified' },
    not_applicable: { bg: 'bg-gray-100', text: 'text-gray-600', label: 'Not Applicable' },
  };
  const cfg = map[status] || { bg: 'bg-gray-100', text: 'text-gray-700', label: status };
  return (
    <span className={`text-xs px-2.5 py-1 rounded-full font-medium ${cfg.bg} ${cfg.text}`}>
      {cfg.label}
    </span>
  );
}
