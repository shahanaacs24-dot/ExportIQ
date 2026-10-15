"""Initial schema — all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-10-15 00:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(254), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # ── msme_profiles ─────────────────────────────────────────
    op.create_table(
        'msme_profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('business_name', sa.String(300), nullable=False),
        sa.Column('gstin', sa.String(15), nullable=True),
        sa.Column('pan', sa.String(10), nullable=True),
        sa.Column('iec_number', sa.String(20), nullable=True),
        sa.Column('udyam_number', sa.String(20), nullable=True),
        sa.Column('category', sa.Enum('micro', 'small', 'medium', name='msmecategory'), nullable=True),
        sa.Column('industry_sector', sa.String(200), nullable=True),
        sa.Column('year_established', sa.Integer(), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('website', sa.String(300), nullable=True),
        sa.Column('has_exported_before', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('export_experience_years', sa.Integer(), nullable=True),
        sa.Column('annual_turnover_inr', sa.Numeric(18, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index('ix_msme_profiles_id', 'msme_profiles', ['id'])
    op.create_index('ix_msme_profiles_gstin', 'msme_profiles', ['gstin'])

    # ── products ──────────────────────────────────────────────
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hs_code', sa.String(12), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_hs_code', 'products', ['hs_code'])

    # ── destination_countries ─────────────────────────────────
    op.create_table(
        'destination_countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('iso_code', sa.String(3), nullable=False),
        sa.Column('iso_code_2', sa.String(2), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('region', sa.String(100), nullable=True),
        sa.Column('trade_bloc', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('iso_code'),
    )
    op.create_index('ix_destination_countries_id', 'destination_countries', ['id'])
    op.create_index('ix_destination_countries_iso_code', 'destination_countries', ['iso_code'])

    # ── requirements ──────────────────────────────────────────
    op.create_table(
        'requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum(
            'legal_registration', 'product_quality', 'trade_documentation',
            'phytosanitary', 'labelling', 'packaging', 'financial', 'logistics',
            name='requirementcategory'), nullable=False),
        sa.Column('applicable_hs_codes', sa.JSON(), nullable=True),
        sa.Column('applicable_country_iso', sa.JSON(), nullable=True),
        sa.Column('applicable_product_categories', sa.JSON(), nullable=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('required_document_types', sa.JSON(), nullable=False),
        sa.Column('evidence_fields', sa.JSON(), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_mandatory', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('issuing_authority', sa.String(300), nullable=True),
        sa.Column('source_url', sa.String(1000), nullable=True),
        sa.Column('source_date', sa.Date(), nullable=True),
        sa.Column('kb_status', sa.Enum('verified', 'unverified', 'deprecated', name='requirementstatus'), nullable=False, server_default='unverified'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index('ix_requirements_id', 'requirements', ['id'])
    op.create_index('ix_requirements_code', 'requirements', ['code'])
    op.create_index('ix_requirements_category', 'requirements', ['category'])

    # ── assessments ───────────────────────────────────────────
    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('destination_country_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('draft', 'in_progress', 'completed', 'archived', name='assessmentstatus'), nullable=False, server_default='draft'),
        sa.Column('eri_score', sa.Float(), nullable=True),
        sa.Column('category_scores', sa.JSON(), nullable=True),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),
        sa.Column('total_requirements', sa.Integer(), nullable=True),
        sa.Column('compliant_count', sa.Integer(), nullable=True),
        sa.Column('missing_count', sa.Integer(), nullable=True),
        sa.Column('incomplete_count', sa.Integer(), nullable=True),
        sa.Column('expired_count', sa.Integer(), nullable=True),
        sa.Column('user_responses', sa.JSON(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['destination_country_id'], ['destination_countries.id']),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assessments_id', 'assessments', ['id'])
    op.create_index('ix_assessments_user_id', 'assessments', ['user_id'])

    # ── documents ─────────────────────────────────────────────
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=True),
        sa.Column('original_filename', sa.String(500), nullable=False),
        sa.Column('stored_filename', sa.String(500), nullable=False),
        sa.Column('file_path', sa.String(1000), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=False),
        sa.Column('document_type', sa.Enum(
            'iec_certificate', 'gstin_certificate', 'udyam_certificate', 'pan_card',
            'certificate_of_incorporation', 'bis_certificate', 'fssai_license',
            'apeda_certificate', 'quality_certificate', 'test_report', 'invoice',
            'packing_list', 'shipping_bill', 'bill_of_lading', 'certificate_of_origin',
            'phytosanitary_certificate', 'health_certificate', 'other',
            name='documenttype'), nullable=False, server_default='other'),
        sa.Column('status', sa.Enum('uploaded', 'processing', 'processed', 'failed', name='documentstatus'), nullable=False, server_default='uploaded'),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extracted_fields', sa.JSON(), nullable=True),
        sa.Column('ocr_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('stored_filename'),
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    op.create_index('ix_documents_user_id', 'documents', ['user_id'])
    op.create_index('ix_documents_assessment_id', 'documents', ['assessment_id'])

    # ── assessment_requirements ───────────────────────────────
    op.create_table(
        'assessment_requirements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('assessment_id', sa.Integer(), nullable=False),
        sa.Column('requirement_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(
            'compliant', 'non_compliant', 'incomplete', 'expired',
            'unverified', 'missing', 'not_applicable',
            name='compliancestatus'), nullable=False, server_default='missing'),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('evidence_document_ids', sa.JSON(), nullable=True),
        sa.Column('matched_fields', sa.JSON(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=False, server_default='0'),
        sa.Column('points_possible', sa.Float(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assessment_id'], ['assessments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['requirement_id'], ['requirements.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assessment_requirements_id', 'assessment_requirements', ['id'])
    op.create_index('ix_assessment_requirements_assessment_id', 'assessment_requirements', ['assessment_id'])


def downgrade() -> None:
    op.drop_table('assessment_requirements')
    op.drop_table('documents')
    op.drop_table('assessments')
    op.drop_table('requirements')
    op.drop_table('destination_countries')
    op.drop_table('products')
    op.drop_table('msme_profiles')
    op.drop_table('users')
    # Drop custom enum types
    sa.Enum(name='compliancestatus').drop(op.get_bind())
    sa.Enum(name='documentstatus').drop(op.get_bind())
    sa.Enum(name='documenttype').drop(op.get_bind())
    sa.Enum(name='assessmentstatus').drop(op.get_bind())
    sa.Enum(name='requirementstatus').drop(op.get_bind())
    sa.Enum(name='requirementcategory').drop(op.get_bind())
    sa.Enum(name='msmecategory').drop(op.get_bind())
