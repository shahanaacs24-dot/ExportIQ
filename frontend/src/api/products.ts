/**
 * Products and destination countries API helpers.
 */
import api from './client';
import type { Product, DestinationCountry } from '../types';

export const productsApi = {
  async listProducts(q?: string): Promise<Product[]> {
    const { data } = await api.get<Product[]>('/products', { params: q ? { q } : {} });
    return data;
  },

  async listDestinations(q?: string): Promise<DestinationCountry[]> {
    const { data } = await api.get<DestinationCountry[]>('/products/destinations', {
      params: q ? { q } : {},
    });
    return data;
  },
};
