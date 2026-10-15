/**
 * Documents and Certificates API helpers.
 */
import api from './client';
import type { Document, DocumentType } from '../types';

export const documentsApi = {
  async list(): Promise<Document[]> {
    const { data } = await api.get<Document[]>('/documents');
    return data;
  },

  async upload(file: File, documentType: DocumentType, assessmentId?: number): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    if (assessmentId) {
      formData.append('assessment_id', assessmentId.toString());
    }
    const { data } = await api.post<Document>('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/documents/${id}`);
  },
};
