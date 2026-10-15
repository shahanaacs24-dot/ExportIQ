import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Building2, Edit2, Save, X, CheckCircle, AlertTriangle } from 'lucide-react';
import toast from 'react-hot-toast';
import { profileApi, type ProfileCreatePayload } from '../api/profile';
import type { MSMEProfile } from '../types';
import Spinner from '../components/ui/Spinner';
import ErrorAlert from '../components/ui/ErrorAlert';
import FormField from '../components/ui/FormField';

const INDIAN_STATES = [
  'Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chhattisgarh','Goa','Gujarat',
  'Haryana','Himachal Pradesh','Jharkhand','Karnataka','Kerala','Madhya Pradesh',
  'Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Punjab','Rajasthan',
  'Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal',
  'Delhi','Jammu & Kashmir','Ladakh','Puducherry','Chandigarh','Other',
];

const INDUSTRY_SECTORS = [
  'Agriculture & Allied','Food Processing','Textiles & Garments','Leather Goods',
  'Chemicals & Pharmaceuticals','Gems & Jewellery','Electronics & IT Hardware',
  'Engineering Goods','Marine Products','Handicrafts','Plastics & Rubber',
  'Paper & Wood Products','Minerals & Mining','Services & Consulting','Other',
];

const schema = z.object({
  business_name: z.string().min(2, 'Business name must be at least 2 characters'),
  gstin: z.string().regex(/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/, 'Invalid GSTIN format').optional().or(z.literal('')),
  pan: z.string().regex(/^[A-Z]{5}[0-9]{4}[A-Z]{1}$/, 'Invalid PAN format').optional().or(z.literal('')),
  iec_number: z.string().max(20).optional().or(z.literal('')),
  udyam_number: z.string().max(20).optional().or(z.literal('')),
  category: z.enum(['micro', 'small', 'medium']).optional().or(z.literal('')),
  industry_sector: z.string().optional().or(z.literal('')),
  year_established: z.coerce.number().int().min(1800).max(2026).optional().or(z.literal('')),
  state: z.string().optional().or(z.literal('')),
  city: z.string().max(100).optional().or(z.literal('')),
  address: z.string().max(500).optional().or(z.literal('')),
  phone: z.string().max(20).optional().or(z.literal('')),
  website: z.string().url('Enter a valid URL (including https://)').optional().or(z.literal('')),
  has_exported_before: z.boolean(),
  export_experience_years: z.coerce.number().int().min(0).max(100).optional().or(z.literal('')),
  annual_turnover_inr: z.coerce.number().min(0).optional().or(z.literal('')),
});

type FormData = z.infer<typeof schema>;

function profileToFormData(p: MSMEProfile): Partial<FormData> {
  return {
    business_name: p.business_name,
    gstin: p.gstin || '',
    pan: p.pan || '',
    iec_number: p.iec_number || '',
    udyam_number: p.udyam_number || '',
    category: (p.category as any) || '',
    industry_sector: p.industry_sector || '',
    year_established: p.year_established || ('' as any),
    state: p.state || '',
    city: p.city || '',
    address: p.address || '',
    phone: p.phone || '',
    website: p.website || '',
    has_exported_before: p.has_exported_before,
    export_experience_years: p.export_experience_years || ('' as any),
    annual_turnover_inr: p.annual_turnover_inr || ('' as any),
  };
}

function cleanPayload(data: FormData): ProfileCreatePayload {
  const clean = (v: any) => (v === '' || v === undefined || v === null ? undefined : v);
  return {
    business_name: data.business_name,
    gstin: clean(data.gstin),
    pan: clean(data.pan),
    iec_number: clean(data.iec_number),
    udyam_number: clean(data.udyam_number),
    category: clean(data.category) as any,
    industry_sector: clean(data.industry_sector),
    year_established: clean(data.year_established) as any,
    state: clean(data.state),
    city: clean(data.city),
    address: clean(data.address),
    phone: clean(data.phone),
    website: clean(data.website),
    has_exported_before: data.has_exported_before,
    export_experience_years: clean(data.export_experience_years) as any,
    annual_turnover_inr: clean(data.annual_turnover_inr) as any,
  };
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<MSMEProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [apiError, setApiError] = useState('');
  const isNew = !profile;

  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema), defaultValues: { has_exported_before: false } });

  const hasExported = watch('has_exported_before');

  useEffect(() => {
    async function load() {
      try {
        const p = await profileApi.get();
        setProfile(p);
        reset(profileToFormData(p));
      } catch (err: any) {
        if (err.response?.status !== 404) {
          setApiError(err.response?.data?.detail || 'Failed to load profile.');
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [reset]);

  const startEdit = () => {
    if (profile) reset(profileToFormData(profile));
    setEditing(true);
    setApiError('');
  };
  const cancelEdit = () => {
    setEditing(false);
    setApiError('');
    if (profile) reset(profileToFormData(profile));
  };

  const onSubmit = async (data: FormData) => {
    setApiError('');
    const payload = cleanPayload(data);
    try {
      const result = isNew
        ? await profileApi.create(payload)
        : await profileApi.update(payload);
      setProfile(result);
      reset(profileToFormData(result));
      setEditing(false);
      toast.success(isNew ? 'Profile created!' : 'Profile updated!');
    } catch (err: any) {
      setApiError(err.response?.data?.detail || 'Failed to save profile.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size="lg" message="Loading profile…" />
      </div>
    );
  }

  const showForm = isNew || editing;

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="bg-brand-100 text-brand-700 p-2.5 rounded-xl">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">MSME Profile</h1>
            <p className="text-sm text-gray-500">
              {isNew ? 'Create your business profile to start assessments' : profile?.business_name}
            </p>
          </div>
        </div>
        {!isNew && !editing && (
          <button
            onClick={startEdit}
            className="inline-flex items-center gap-2 px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700 transition-colors"
          >
            <Edit2 className="w-4 h-4" />
            Edit Profile
          </button>
        )}
      </div>

      {!isNew && !editing && (
        <div className="mb-6 bg-green-50 border border-green-200 rounded-xl p-4 flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-green-800">Profile complete</p>
            <p className="text-xs text-green-600 mt-0.5">
              Your MSME profile is set up. You can now run export readiness assessments.
            </p>
          </div>
        </div>
      )}

      {isNew && (
        <div className="mb-6 bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-800">Profile not yet created</p>
            <p className="text-xs text-amber-700 mt-0.5">
              Create your MSME profile to run export readiness assessments.
            </p>
          </div>
        </div>
      )}

      {apiError && (
        <div className="mb-6">
          <ErrorAlert message={apiError} onDismiss={() => setApiError('')} />
        </div>
      )}

      {!showForm && profile && (
        <ProfileReadView profile={profile} />
      )}

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8" noValidate>
          <section className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-5">Organisation Details</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="sm:col-span-2">
                <FormField label="Business / Trade Name" htmlFor="business_name" error={errors.business_name?.message} required>
                  <input
                    id="business_name"
                    type="text"
                    {...register('business_name')}
                    className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${errors.business_name ? 'border-red-400' : 'border-gray-300'}`}
                    placeholder="e.g. Sunrise Exports Pvt. Ltd."
                  />
                </FormField>
              </div>
              <FormField label="GSTIN" htmlFor="gstin" error={errors.gstin?.message} hint="15-character GST Identification Number">
                <input id="gstin" type="text" {...register('gstin')} placeholder="22AAAAA0000A1Z5"
                  className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 uppercase ${errors.gstin ? 'border-red-400' : 'border-gray-300'}`} />
              </FormField>
              <FormField label="PAN" htmlFor="pan" error={errors.pan?.message} hint="10-character PAN">
                <input id="pan" type="text" {...register('pan')} placeholder="AAAAA1234A"
                  className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 uppercase ${errors.pan ? 'border-red-400' : 'border-gray-300'}`} />
              </FormField>
              <FormField label="IEC Number" htmlFor="iec_number" hint="Import Export Code from DGFT">
                <input id="iec_number" type="text" {...register('iec_number')} placeholder="AABCS1429B"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </FormField>
              <FormField label="Udyam Registration No." htmlFor="udyam_number" hint="e.g. UDYAM-TN-01-0000001">
                <input id="udyam_number" type="text" {...register('udyam_number')} placeholder="UDYAM-XX-00-0000000"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </FormField>
              <FormField label="MSME Category" htmlFor="category">
                <select id="category" {...register('category')}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white">
                  <option value="">Select category…</option>
                  <option value="micro">Micro</option>
                  <option value="small">Small</option>
                  <option value="medium">Medium</option>
                </select>
              </FormField>
              <FormField label="Industry Sector" htmlFor="industry_sector">
                <select id="industry_sector" {...register('industry_sector')}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white">
                  <option value="">Select sector…</option>
                  {INDUSTRY_SECTORS.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </FormField>
              <FormField label="Year Established" htmlFor="year_established" error={errors.year_established?.message}>
                <input id="year_established" type="number" {...register('year_established')} placeholder="e.g. 2010" min={1800} max={2026}
                  className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${errors.year_established ? 'border-red-400' : 'border-gray-300'}`} />
              </FormField>
            </div>
          </section>

          <section className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-5">Contact Information</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <FormField label="State" htmlFor="state">
                <select id="state" {...register('state')}
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white">
                  <option value="">Select state…</option>
                  {INDIAN_STATES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </FormField>
              <FormField label="City" htmlFor="city">
                <input id="city" type="text" {...register('city')} placeholder="e.g. Surat"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </FormField>
              <div className="sm:col-span-2">
                <FormField label="Address" htmlFor="address">
                  <textarea id="address" rows={2} {...register('address')} placeholder="Registered office address"
                    className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none" />
                </FormField>
              </div>
              <FormField label="Phone" htmlFor="phone">
                <input id="phone" type="tel" {...register('phone')} placeholder="+91 98765 43210"
                  className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500" />
              </FormField>
              <FormField label="Website" htmlFor="website" error={errors.website?.message} hint="Include https://">
                <input id="website" type="url" {...register('website')} placeholder="https://yourcompany.in"
                  className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${errors.website ? 'border-red-400' : 'border-gray-300'}`} />
              </FormField>
            </div>
          </section>

          <section className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-5">Export Experience & Financials</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              <div className="sm:col-span-2">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" {...register('has_exported_before')}
                    className="w-4 h-4 accent-brand-600" />
                  <span className="text-sm font-medium text-gray-700">
                    Our company has exported products before
                  </span>
                </label>
              </div>
              {hasExported && (
                <FormField label="Years of Export Experience" htmlFor="export_experience_years" error={errors.export_experience_years?.message}>
                  <input id="export_experience_years" type="number" {...register('export_experience_years')} placeholder="0" min={0} max={100}
                    className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${errors.export_experience_years ? 'border-red-400' : 'border-gray-300'}`} />
                </FormField>
              )}
              <FormField label="Annual Turnover (₹)" htmlFor="annual_turnover_inr" error={errors.annual_turnover_inr?.message} hint="In Indian Rupees">
                <input id="annual_turnover_inr" type="number" {...register('annual_turnover_inr')} placeholder="e.g. 5000000"
                  className={`w-full px-3 py-2.5 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 ${errors.annual_turnover_inr ? 'border-red-400' : 'border-gray-300'}`} />
              </FormField>
            </div>
          </section>

          <div className="flex items-center gap-3 justify-end pb-8">
            {!isNew && (
              <button type="button" onClick={cancelEdit}
                className="inline-flex items-center gap-2 px-5 py-2.5 border border-gray-300 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 transition-colors">
                <X className="w-4 h-4" /> Cancel
              </button>
            )}
            <button type="submit" disabled={isSubmitting}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-700 disabled:bg-brand-300 text-white text-sm font-semibold rounded-lg transition-colors">
              {isSubmitting ? <Spinner size="sm" /> : <Save className="w-4 h-4" />}
              {isSubmitting ? 'Saving…' : isNew ? 'Create Profile' : 'Save Changes'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

function ProfileReadView({ profile }: { profile: MSMEProfile }) {
  const fmt = (v: any, fallback = '—') => (v !== null && v !== undefined && v !== '' ? v : fallback);
  const fmtBool = (v: boolean) => (v ? 'Yes' : 'No');
  const fmtCurrency = (v: number | null | undefined) =>
    v ? `₹ ${Number(v).toLocaleString('en-IN')}` : '—';

  return (
    <div className="space-y-6">
      <ProfileSection title="Organisation Details" items={[
        { label: 'Business Name', value: fmt(profile.business_name) },
        { label: 'GSTIN', value: fmt(profile.gstin) },
        { label: 'PAN', value: fmt(profile.pan) },
        { label: 'IEC Number', value: fmt(profile.iec_number) },
        { label: 'Udyam Registration', value: fmt(profile.udyam_number) },
        { label: 'MSME Category', value: profile.category ? profile.category.charAt(0).toUpperCase() + profile.category.slice(1) : '—' },
        { label: 'Industry Sector', value: fmt(profile.industry_sector) },
        { label: 'Year Established', value: fmt(profile.year_established) },
      ]} />
      <ProfileSection title="Contact Information" items={[
        { label: 'State', value: fmt(profile.state) },
        { label: 'City', value: fmt(profile.city) },
        { label: 'Address', value: fmt(profile.address) },
        { label: 'Phone', value: fmt(profile.phone) },
        { label: 'Website', value: profile.website ? profile.website : '—' },
      ]} />
      <ProfileSection title="Export Experience" items={[
        { label: 'Exported Before', value: fmtBool(profile.has_exported_before) },
        { label: 'Export Experience', value: profile.export_experience_years ? `${profile.export_experience_years} year(s)` : '—' },
        { label: 'Annual Turnover', value: fmtCurrency(profile.annual_turnover_inr) },
      ]} />
    </div>
  );
}

function ProfileSection({ title, items }: { title: string; items: { label: string; value: string }[] }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
      </div>
      <dl className="divide-y divide-gray-100">
        {items.map(({ label, value }) => (
          <div key={label} className="px-6 py-3 flex flex-col sm:flex-row sm:gap-4">
            <dt className="text-xs font-medium text-gray-500 sm:w-48 shrink-0">{label}</dt>
            <dd className="text-sm text-gray-900 mt-0.5 sm:mt-0">{value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
