import React, { useEffect, useState } from 'react';
import { FileText, Upload, Trash2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { documentsApi } from '../api/documents';
import type { Document, DocumentType } from '../types';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

const DOC_TYPES: { value: DocumentType; label: string }[] = [
  { value: 'iec_certificate', label: 'IEC Certificate' },
  { value: 'gstin_certificate', label: 'GSTIN Registration Certificate' },
  { value: 'udyam_certificate', label: 'Udyam Registration' },
  { value: 'fssai_license', label: 'FSSAI License' },
  { value: 'apeda_certificate', label: 'APEDA Registration' },
  { value: 'phytosanitary_certificate', label: 'Phytosanitary Certificate' },
  { value: 'certificate_of_origin', label: 'Certificate of Origin' },
  { value: 'quality_certificate', label: 'Quality Certificate' },
  { value: 'test_report', label: 'Test Report' },
  { value: 'other', label: 'Other Document' },
];

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploading, setUploading] = useState(false);

  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<DocumentType>('iec_certificate');

  const loadDocs = async () => {
    try {
      const data = await documentsApi.list();
      setDocuments(data);
    } catch {
      setError('Failed to load documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDocs(); }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      toast.error('Please select a file to upload.');
      return;
    }
    setUploading(true);
    try {
      await documentsApi.upload(file, docType);
      toast.success('Document uploaded and processed successfully!');
      setFile(null);
      loadDocs();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    try {
      await documentsApi.delete(id);
      toast.success('Document deleted');
      setDocuments(prev => prev.filter(d => d.id !== id));
    } catch {
      toast.error('Failed to delete document');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size="lg" message="Loading documents…" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Documents & Certificates</h1>
        <p className="text-sm text-gray-500 mt-1">
          Upload compliance certificates (IEC, GST, FSSAI, APEDA, etc.). ExportIQ automatically extracts key fields to satisfy assessment requirements.
        </p>
      </div>

      {error && <ErrorAlert message={error} onDismiss={() => setError('')} />}

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Upload className="w-5 h-5 text-brand-600" />
          Upload Compliance Document
        </h2>
        <form onSubmit={handleUpload} className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Document Type</label>
            <select
              value={docType}
              onChange={e => setDocType(e.target.value as DocumentType)}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm bg-white focus:ring-2 focus:ring-brand-500"
            >
              {DOC_TYPES.map(t => (
                <option key={t.value} value={t.value}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">PDF or Image File</label>
            <input
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.tiff"
              onChange={e => setFile(e.target.files?.[0] || null)}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={uploading || !file}
              className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:bg-brand-300 transition-colors"
            >
              {uploading && <Spinner size="sm" />}
              {uploading ? 'Processing…' : 'Upload & Parse'}
            </button>
          </div>
        </form>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-600" />
            Uploaded Documents ({documents.length})
          </h2>
          <button
            onClick={() => { setLoading(true); loadDocs(); }}
            className="text-xs text-brand-600 hover:underline inline-flex items-center gap-1 font-medium"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Refresh
          </button>
        </div>

        {documents.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-200">
            <FileText className="w-10 h-10 text-gray-300 mx-auto mb-2" />
            <p className="text-sm font-medium text-gray-700">No documents uploaded yet</p>
            <p className="text-xs text-gray-500 mt-1">Upload certificates above to satisfy export requirements.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {documents.map(d => (
              <div key={d.id} className="py-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-semibold text-gray-900">{d.original_filename}</span>
                    <span className="text-xs px-2 py-0.5 rounded font-medium bg-brand-50 text-brand-700">
                      {d.document_type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                      d.status === 'processed' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                    }`}>
                      {d.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500">
                    Size: {(d.file_size_bytes / 1024).toFixed(1)} KB · Uploaded {new Date(d.created_at).toLocaleDateString()}
                  </p>
                  {d.extracted_fields && Object.keys(d.extracted_fields).length > 0 && (
                    <div className="mt-2 text-xs bg-gray-50 p-2.5 rounded-lg border border-gray-200 font-mono text-gray-700">
                      <span className="font-semibold text-gray-900">Extracted Fields:</span>{' '}
                      {JSON.stringify(d.extracted_fields)}
                    </div>
                  )}
                </div>

                <button
                  onClick={() => handleDelete(d.id)}
                  className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-gray-50 transition-colors"
                  title="Delete Document"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
