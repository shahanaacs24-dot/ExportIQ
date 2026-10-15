/**
 * MSME Profile API helpers.
 */
import api from './client';
import type { MSMEProfile } from '../types';

export interface ProfileCreatePayload {
  business_name: string;
  gstin?: string;
  pan?: string;
  iec_number?: string;
  udyam_number?: string;
  category?: 'micro' | 'small' | 'medium';
  industry_sector?: string;
  year_established?: number;
  state?: string;
  city?: string;
  address?: string;
  phone?: string;
  website?: string;
  has_exported_before: boolean;
  export_experience_years?: number;
  annual_turnover_inr?: number;
}

export const profileApi = {
  async get(): Promise<MSMEProfile> {
    const { data } = await api.get<MSMEProfile>('/profile');
    return data;
  },

  async create(payload: ProfileCreatePayload): Promise<MSMEProfile> {
    const { data } = await api.post<MSMEProfile>('/profile', payload);
    return data;
  },

  async update(payload: Partial<ProfileCreatePayload>): Promise<MSMEProfile> {
    const { data } = await api.patch<MSMEProfile>('/profile', payload);
    return data;
  },
};
