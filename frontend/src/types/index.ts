// TypeScript types mirroring backend Pydantic schemas

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface MSMEProfile {
  id: number;
  user_id: number;
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
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: number;
  hs_code: string;
  name: string;
  description?: string;
  category?: string;
}

export interface DestinationCountry {
  id: number;
  iso_code: string;
  iso_code_2: string;
  name: string;
  region?: string;
  trade_bloc?: string;
}

export type DocumentType =
  | 'iec_certificate'
  | 'gstin_certificate'
  | 'udyam_certificate'
  | 'pan_card'
  | 'certificate_of_incorporation'
  | 'bis_certificate'
  | 'fssai_license'
  | 'apeda_certificate'
  | 'quality_certificate'
  | 'test_report'
  | 'invoice'
  | 'packing_list'
  | 'shipping_bill'
  | 'bill_of_lading'
  | 'certificate_of_origin'
  | 'phytosanitary_certificate'
  | 'health_certificate'
  | 'other';

export type DocumentStatus = 'uploaded' | 'processing' | 'processed' | 'failed';

export interface Document {
  id: number;
  user_id: number;
  assessment_id?: number;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;
  document_type: DocumentType;
  status: DocumentStatus;
  extracted_fields?: Record<string, unknown>;
  ocr_used: boolean;
  processing_error?: string;
  created_at: string;
  updated_at: string;
}

export type AssessmentStatus = 'draft' | 'in_progress' | 'completed' | 'archived';

export type ComplianceStatus =
  | 'compliant'
  | 'non_compliant'
  | 'incomplete'
  | 'expired'
  | 'unverified'
  | 'missing'
  | 'not_applicable';

export interface RequirementResult {
  id: number;
  requirement_id: number;
  status: ComplianceStatus;
  explanation?: string;
  points_earned: number;
  points_possible: number;
}

export interface Assessment {
  id: number;
  user_id: number;
  product_id: number;
  destination_country_id: number;
  status: AssessmentStatus;
  eri_score?: number;
  total_requirements?: number;
  compliant_count?: number;
  missing_count?: number;
  incomplete_count?: number;
  expired_count?: number;
  category_scores?: Record<string, number>;
  score_breakdown?: Record<string, unknown>;
  user_responses?: Record<string, unknown>;
  submitted_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  requirement_results?: RequirementResult[];
}

export interface ApiError {
  detail: string;
}
