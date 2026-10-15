import { useEffect, useState, useCallback } from 'react';
import { Package, Globe, Search, CheckCircle2 } from 'lucide-react';
import { productsApi } from '../api/products';
import type { Product, DestinationCountry } from '../types';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [productSearch, setProductSearch] = useState('');
  const [productsLoading, setProductsLoading] = useState(true);
  const [productsError, setProductsError] = useState('');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);

  const [destinations, setDestinations] = useState<DestinationCountry[]>([]);
  const [destSearch, setDestSearch] = useState('');
  const [destsLoading, setDestsLoading] = useState(true);
  const [destsError, setDestsError] = useState('');
  const [selectedDest, setSelectedDest] = useState<DestinationCountry | null>(null);

  const loadProducts = useCallback(async (q: string) => {
    setProductsLoading(true);
    setProductsError('');
    try {
      const data = await productsApi.listProducts(q || undefined);
      setProducts(data);
    } catch {
      setProductsError('Failed to load products. Ensure the backend is running.');
    } finally {
      setProductsLoading(false);
    }
  }, []);

  const loadDestinations = useCallback(async (q: string) => {
    setDestsLoading(true);
    setDestsError('');
    try {
      const data = await productsApi.listDestinations(q || undefined);
      setDestinations(data);
    } catch {
      setDestsError('Failed to load destinations. Ensure the backend is running.');
    } finally {
      setDestsLoading(false);
    }
  }, []);

  useEffect(() => { loadProducts(''); }, [loadProducts]);
  useEffect(() => { loadDestinations(''); }, [loadDestinations]);

  useEffect(() => {
    const t = setTimeout(() => loadProducts(productSearch), 300);
    return () => clearTimeout(t);
  }, [productSearch, loadProducts]);

  useEffect(() => {
    const t = setTimeout(() => loadDestinations(destSearch), 300);
    return () => clearTimeout(t);
  }, [destSearch, loadDestinations]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Products & Destinations</h1>
        <p className="text-sm text-gray-500 mt-1">
          Browse supported export products and destination countries. Select one of each to begin an assessment.
        </p>
      </div>

      {(selectedProduct || selectedDest) && (
        <div className="bg-brand-50 border border-brand-200 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex-1 space-y-1">
            {selectedProduct && (
              <p className="text-sm text-brand-800">
                <span className="font-medium">Product:</span> {selectedProduct.name} <span className="text-brand-500 text-xs">(HS: {selectedProduct.hs_code})</span>
              </p>
            )}
            {selectedDest && (
              <p className="text-sm text-brand-800">
                <span className="font-medium">Destination:</span> {selectedDest.name} <span className="text-brand-500 text-xs">({selectedDest.iso_code})</span>
              </p>
            )}
          </div>
          {selectedProduct && selectedDest && (
            <a
              href="/assessments"
              className="inline-flex items-center gap-2 px-5 py-2 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 transition-colors"
            >
              <CheckCircle2 className="w-4 h-4" />
              Start Assessment
            </a>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <Package className="w-5 h-5 text-brand-600" />
              Export Products
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-normal ml-1">
                {products.length} available
              </span>
            </h2>
          </div>

          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by name or HS code…"
              value={productSearch}
              onChange={e => setProductSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              aria-label="Search products"
            />
          </div>

          {productsError && <ErrorAlert message={productsError} onDismiss={() => setProductsError('')} />}

          {productsLoading ? (
            <div className="bg-white border border-gray-200 rounded-xl p-8 flex justify-center">
              <Spinner message="Loading products…" />
            </div>
          ) : products.length === 0 ? (
            <EmptyState
              icon={<Package className="w-10 h-10 text-gray-300" />}
              title="No products found"
              description={productSearch ? `No match for "${productSearch}". Try a different search.` : 'No products are available.'}
              action={productSearch ? <button onClick={() => setProductSearch('')} className="text-sm text-brand-600 hover:underline">Clear search</button> : null}
            />
          ) : (
            <ul className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 overflow-hidden shadow-sm">
              {products.map(p => (
                <li key={p.id}>
                  <button
                    onClick={() => setSelectedProduct(prev => prev?.id === p.id ? null : p)}
                    className={`w-full text-left px-4 py-3.5 hover:bg-gray-50 transition-colors flex items-start gap-3 ${selectedProduct?.id === p.id ? 'bg-brand-50 border-l-4 border-brand-600' : ''}`}
                    aria-pressed={selectedProduct?.id === p.id}
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{p.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        HS {p.hs_code} {p.category && `· ${p.category}`}
                      </p>
                    </div>
                    {selectedProduct?.id === p.id && (
                      <CheckCircle2 className="w-5 h-5 text-brand-600 flex-shrink-0 mt-0.5" />
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-gray-900 flex items-center gap-2">
              <Globe className="w-5 h-5 text-brand-600" />
              Destination Countries
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full font-normal ml-1">
                {destinations.length} available
              </span>
            </h2>
          </div>

          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            <input
              type="text"
              placeholder="Search by name or ISO code…"
              value={destSearch}
              onChange={e => setDestSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
              aria-label="Search destinations"
            />
          </div>

          {destsError && <ErrorAlert message={destsError} onDismiss={() => setDestsError('')} />}

          {destsLoading ? (
            <div className="bg-white border border-gray-200 rounded-xl p-8 flex justify-center">
              <Spinner message="Loading countries…" />
            </div>
          ) : destinations.length === 0 ? (
            <EmptyState
              icon={<Globe className="w-10 h-10 text-gray-300" />}
              title="No countries found"
              description={destSearch ? `No match for "${destSearch}".` : 'No destination countries available.'}
              action={destSearch ? <button onClick={() => setDestSearch('')} className="text-sm text-brand-600 hover:underline">Clear search</button> : null}
            />
          ) : (
            <ul className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 overflow-hidden shadow-sm">
              {destinations.map(c => (
                <li key={c.id}>
                  <button
                    onClick={() => setSelectedDest(prev => prev?.id === c.id ? null : c)}
                    className={`w-full text-left px-4 py-3.5 hover:bg-gray-50 transition-colors flex items-start gap-3 ${selectedDest?.id === c.id ? 'bg-brand-50 border-l-4 border-brand-600' : ''}`}
                    aria-pressed={selectedDest?.id === c.id}
                  >
                    <span className="text-2xl leading-none flex-shrink-0">{countryFlag(c.iso_code_2)}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{c.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {c.iso_code} {c.region && `· ${c.region}`} {c.trade_bloc && `· ${c.trade_bloc}`}
                      </p>
                    </div>
                    {selectedDest?.id === c.id && (
                      <CheckCircle2 className="w-5 h-5 text-brand-600 flex-shrink-0 mt-0.5" />
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ icon, title, description, action }: { icon: React.ReactNode; title: string; description: string; action?: React.ReactNode }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-10 text-center">
      <div className="flex justify-center mb-3">{icon}</div>
      <p className="text-sm font-medium text-gray-700">{title}</p>
      <p className="text-xs text-gray-500 mt-1">{description}</p>
      {action && <div className="mt-3">{action}</div>}
    </div>
  );
}

function countryFlag(iso2: string): string {
  if (!iso2 || iso2.length !== 2) return '🌐';
  return String.fromCodePoint(
    ...iso2.toUpperCase().split('').map(c => 0x1F1E6 + c.charCodeAt(0) - 65)
  );
}
