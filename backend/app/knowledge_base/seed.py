"""
ExportIQ — Seed script.
Populates products, destination countries, and the initial requirements knowledge base.

All requirements are drawn from publicly available official sources and are marked
with their verification status. Unverified requirements must be confirmed with the
relevant authority before acting on them.

Run: python -m app.knowledge_base.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import SessionLocal, engine, Base
from app.models import *
from app.models.product import Product, DestinationCountry
from app.models.requirement import Requirement, RequirementCategory, RequirementStatus

import datetime


def seed():
    db = SessionLocal()
    try:
        # ── Products ─────────────────────────────────────────────
        products = [
            Product(hs_code="100630", name="Rice (milled)", category="Agri - Cereals",
                    description="Milled rice, including polished or glazed rice (HS 1006.30)"),
            Product(hs_code="030613", name="Shrimps and Prawns (frozen)", category="Marine Products",
                    description="Frozen shrimps and prawns (HS 0306.13)"),
            Product(hs_code="610910", name="T-shirts (cotton)", category="Textiles & Garments",
                    description="T-shirts, singlets and other vests, of cotton, knitted (HS 6109.10)"),
            Product(hs_code="711319", name="Jewellery (precious metal)", category="Gems & Jewellery",
                    description="Articles of jewellery of other precious metal (HS 7113.19)"),
            Product(hs_code="300490", name="Pharmaceutical preparations", category="Pharmaceuticals",
                    description="Other medicaments (HS 3004.90)"),
            Product(hs_code="854231", name="Electronic integrated circuits", category="Electronics",
                    description="Processors and controllers, electronic integrated circuits (HS 8542.31)"),
            Product(hs_code="420211", name="Leather handbags", category="Leather Goods",
                    description="Handbags with outer surface of leather (HS 4202.11)"),
            Product(hs_code="090111", name="Coffee (not roasted)", category="Agri - Beverages",
                    description="Coffee, not roasted, not decaffeinated (HS 0901.11)"),
        ]
        for p in products:
            if not db.query(Product).filter(Product.hs_code == p.hs_code).first():
                db.add(p)

        # ── Destination Countries ─────────────────────────────────
        countries = [
            DestinationCountry(iso_code="USA", iso_code_2="US", name="United States of America",
                               region="North America", trade_bloc=None),
            DestinationCountry(iso_code="GBR", iso_code_2="GB", name="United Kingdom",
                               region="Europe", trade_bloc=None),
            DestinationCountry(iso_code="DEU", iso_code_2="DE", name="Germany",
                               region="Europe", trade_bloc="EU"),
            DestinationCountry(iso_code="ARE", iso_code_2="AE", name="United Arab Emirates",
                               region="Middle East", trade_bloc="GCC"),
            DestinationCountry(iso_code="SGP", iso_code_2="SG", name="Singapore",
                               region="Southeast Asia", trade_bloc="ASEAN"),
            DestinationCountry(iso_code="AUS", iso_code_2="AU", name="Australia",
                               region="Oceania", trade_bloc=None),
            DestinationCountry(iso_code="JPN", iso_code_2="JP", name="Japan",
                               region="East Asia", trade_bloc=None),
            DestinationCountry(iso_code="CAN", iso_code_2="CA", name="Canada",
                               region="North America", trade_bloc=None),
            DestinationCountry(iso_code="BGD", iso_code_2="BD", name="Bangladesh",
                               region="South Asia", trade_bloc="SAARC"),
            DestinationCountry(iso_code="NLD", iso_code_2="NL", name="Netherlands",
                               region="Europe", trade_bloc="EU"),
        ]
        for c in countries:
            if not db.query(DestinationCountry).filter(DestinationCountry.iso_code == c.iso_code).first():
                db.add(c)

        db.flush()

        # ── Requirements Knowledge Base ───────────────────────────
        # NOTE: Requirements are based on publicly available information from
        # DGFT, FSSAI, APEDA, BIS, and destination country customs portals.
        # Source dates and verification status reflect the state at time of entry.
        # Users MUST verify current requirements with the issuing authority before export.
        requirements = [
            # ── Legal Registration (India) ────────────────────────
            Requirement(
                code="IND-IEC-001",
                name="Import Export Code (IEC)",
                description=(
                    "Every exporter from India must obtain an Import Export Code (IEC) "
                    "from the Directorate General of Foreign Trade (DGFT), Government of India. "
                    "IEC is mandatory for all exports unless specifically exempted."
                ),
                category=RequirementCategory.LEGAL_REGISTRATION,
                applicable_hs_codes=None,  # all products
                applicable_country_iso=None,  # all destinations
                required_document_types=["iec_certificate"],
                evidence_fields=["iec_number", "business_name", "validity_date"],
                weight=10,
                is_mandatory=True,
                issuing_authority="Directorate General of Foreign Trade (DGFT), Ministry of Commerce, India",
                source_url="https://www.dgft.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="IEC is lifelong; no renewal required. Verify current exemptions via DGFT portal.",
            ),
            Requirement(
                code="IND-GST-001",
                name="GST Registration / GSTIN",
                description=(
                    "Exporters are required to be registered under GST. The GSTIN must be "
                    "quoted on export invoices. Exports are zero-rated under GST, but "
                    "registration is mandatory for claiming refund of input tax credit."
                ),
                category=RequirementCategory.LEGAL_REGISTRATION,
                applicable_hs_codes=None,
                applicable_country_iso=None,
                required_document_types=["gstin_certificate"],
                evidence_fields=["gstin", "business_name"],
                weight=8,
                is_mandatory=True,
                issuing_authority="Goods and Services Tax Network (GSTN), India",
                source_url="https://www.gst.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="GSTIN must match across all export documents.",
            ),
            Requirement(
                code="IND-UDYAM-001",
                name="Udyam Registration",
                description=(
                    "MSMEs should be registered on the Udyam Registration Portal to avail "
                    "government schemes and priority sector export benefits. While not strictly "
                    "mandatory for export, it is required for MSME-specific incentives and schemes."
                ),
                category=RequirementCategory.LEGAL_REGISTRATION,
                applicable_hs_codes=None,
                applicable_country_iso=None,
                required_document_types=["udyam_certificate"],
                evidence_fields=["udyam_number", "category", "business_name"],
                weight=4,
                is_mandatory=False,
                issuing_authority="Ministry of Micro, Small and Medium Enterprises, India",
                source_url="https://udyamregistration.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Recommended for MSME benefits; not mandatory for export clearance.",
            ),

            # ── Agri / Food Products ──────────────────────────────
            Requirement(
                code="IND-FSSAI-001",
                name="FSSAI License / Registration",
                description=(
                    "Exporters of food products (including processed food, beverages, spices, "
                    "and agricultural produce intended for human consumption) must hold a valid "
                    "FSSAI license or registration as applicable. The FSSAI license number must "
                    "appear on export packaging."
                ),
                category=RequirementCategory.PRODUCT_QUALITY,
                applicable_hs_codes=["02", "03", "04", "07", "08", "09", "10", "11", "12", "15",
                                      "16", "17", "18", "19", "20", "21", "22"],
                applicable_country_iso=None,
                required_document_types=["fssai_license"],
                evidence_fields=["fssai_license_number", "validity_date", "business_name"],
                weight=9,
                is_mandatory=True,
                issuing_authority="Food Safety and Standards Authority of India (FSSAI)",
                source_url="https://foscos.fssai.gov.in/",
                source_date=datetime.date(2024, 6, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="License categories: Registration (turnover < 12L), State License (12L–20Cr), Central License (>20Cr or export).",
            ),
            Requirement(
                code="IND-APEDA-001",
                name="APEDA Registration",
                description=(
                    "Exporters of scheduled products under APEDA (Agricultural and Processed "
                    "Food Products Export Development Authority) must be registered with APEDA. "
                    "Scheduled products include rice, fruits, vegetables, meat, dairy, processed "
                    "food, floriculture, and related products."
                ),
                category=RequirementCategory.LEGAL_REGISTRATION,
                applicable_hs_codes=["02", "03", "04", "07", "08", "09", "10", "11", "16", "20", "21"],
                applicable_country_iso=None,
                required_document_types=["apeda_certificate"],
                evidence_fields=["apeda_registration_number", "validity_date"],
                weight=7,
                is_mandatory=True,
                issuing_authority="Agricultural and Processed Food Products Export Development Authority (APEDA)",
                source_url="https://apeda.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Required for all APEDA-scheduled products. Registration valid for 5 years.",
            ),
            Requirement(
                code="IND-PHYTO-001",
                name="Phytosanitary Certificate",
                description=(
                    "A Phytosanitary Certificate issued by the Plant Protection Adviser of India "
                    "(PPAI) / State Agriculture Departments is required for export of plant and "
                    "plant products to confirm they are free from pests and diseases, as required "
                    "by the importing country's plant quarantine regulations."
                ),
                category=RequirementCategory.PHYTOSANITARY,
                applicable_hs_codes=["06", "07", "08", "09", "10", "11", "12"],
                applicable_country_iso=None,
                required_document_types=["phytosanitary_certificate"],
                evidence_fields=["certificate_number", "issue_date", "consignment_details"],
                weight=8,
                is_mandatory=True,
                issuing_authority="Directorate of Plant Protection, Quarantine & Storage, Ministry of Agriculture, India",
                source_url="https://ppqs.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Required per shipment; validity typically 14–21 days from issuance.",
            ),

            # ── Marine Products ───────────────────────────────────
            Requirement(
                code="IND-MPEDA-001",
                name="MPEDA Registration (Marine Products)",
                description=(
                    "Exporters of marine products must be registered with the Marine Products "
                    "Export Development Authority (MPEDA) and obtain the necessary processing "
                    "plant approval. All seafood export facilities must be MPEDA-approved."
                ),
                category=RequirementCategory.LEGAL_REGISTRATION,
                applicable_hs_codes=["03", "1604", "1605"],
                applicable_country_iso=None,
                required_document_types=["apeda_certificate"],  # using generic quality cert
                evidence_fields=["mpeda_registration_number"],
                weight=9,
                is_mandatory=True,
                issuing_authority="Marine Products Export Development Authority (MPEDA)",
                source_url="https://mpeda.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Processing plants must have HACCP certification for EU/US markets.",
            ),
            Requirement(
                code="IND-HEALTH-001",
                name="Health Certificate (Marine / Animal Products)",
                description=(
                    "A Health Certificate issued by the competent authority (MPEDA / EIC / "
                    "FSSAI) is required by most importing countries for marine and animal "
                    "products to certify they are fit for human consumption and free from "
                    "specified pathogens."
                ),
                category=RequirementCategory.PRODUCT_QUALITY,
                applicable_hs_codes=["02", "03", "04", "1601", "1602", "1604", "1605"],
                applicable_country_iso=None,
                required_document_types=["health_certificate"],
                evidence_fields=["certificate_number", "issue_date", "issuing_authority"],
                weight=8,
                is_mandatory=True,
                issuing_authority="Export Inspection Council (EIC) / MPEDA / FSSAI",
                source_url="https://www.eicindia.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Required per consignment. Specific pathogens tested vary by destination.",
            ),

            # ── Trade Documentation ───────────────────────────────
            Requirement(
                code="IND-TRADE-001",
                name="Certificate of Origin",
                description=(
                    "A Certificate of Origin (COO) certifying that goods were produced or "
                    "manufactured in India is required by most importing countries. It may be "
                    "a non-preferential COO (general trade) or a preferential COO (to claim "
                    "reduced duty under FTAs such as ASEAN-India, India-UAE CEPA, etc.)."
                ),
                category=RequirementCategory.TRADE_DOCUMENTATION,
                applicable_hs_codes=None,
                applicable_country_iso=None,
                required_document_types=["certificate_of_origin"],
                evidence_fields=["origin_country", "exporter_name", "issue_date"],
                weight=6,
                is_mandatory=True,
                issuing_authority="Export Inspection Council (EIC) / Chambers of Commerce / FIEO",
                source_url="https://www.eicindia.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Preferential COO required to claim FTA benefits. Applicable FTA depends on destination.",
            ),

            # ── Destination-Specific ──────────────────────────────
            Requirement(
                code="USA-FDA-001",
                name="US FDA Prior Notice (Food Exports to USA)",
                description=(
                    "Exporters of food products (including dietary supplements, beverages, and "
                    "seafood) to the United States must submit Prior Notice to the US FDA before "
                    "the shipment arrives. The facility must also be registered with the FDA."
                ),
                category=RequirementCategory.TRADE_DOCUMENTATION,
                applicable_hs_codes=["02", "03", "04", "07", "08", "09", "10", "16", "17", "18",
                                      "19", "20", "21", "22"],
                applicable_country_iso=["USA"],
                required_document_types=["health_certificate"],
                evidence_fields=["fda_registration_number", "prior_notice_confirmation"],
                weight=9,
                is_mandatory=True,
                issuing_authority="U.S. Food and Drug Administration (FDA)",
                source_url="https://www.fda.gov/food/guidance-regulation-food-and-dietary-supplements/prior-notice",
                source_date=datetime.date(2024, 6, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes=(
                    "Prior Notice must be submitted 8h before arrival for land, 4h for air, "
                    "8h for other modes. FDA registration is mandatory for food facilities."
                ),
            ),
            Requirement(
                code="EU-TRACES-001",
                name="TRACES NT Registration (EU Food/Animal Products)",
                description=(
                    "Exporters of food of animal origin, animal by-products, and certain plant "
                    "products to the EU must use the TRACES NT system for health certificates "
                    "and official notifications. The Indian exporting establishment must be "
                    "listed on the EU's approved third-country establishment list."
                ),
                category=RequirementCategory.TRADE_DOCUMENTATION,
                applicable_hs_codes=["02", "03", "04", "1601", "1602", "1604", "1605"],
                applicable_country_iso=["DEU", "NLD", "FRA", "ITA", "ESP", "POL", "BEL",
                                        "AUT", "SWE", "DNK", "FIN", "GRC", "IRL", "PRT"],
                required_document_types=["health_certificate"],
                evidence_fields=["traces_establishment_number"],
                weight=9,
                is_mandatory=True,
                issuing_authority="European Commission DG SANTE / TRACES NT",
                source_url="https://food.ec.europa.eu/animals/traces_en",
                source_date=datetime.date(2024, 6, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes=(
                    "Establishment must be listed on EU approved list. "
                    "Not all Indian seafood establishments are listed; verify before export."
                ),
            ),
            Requirement(
                code="UAE-COO-001",
                name="Certificate of Origin (India-UAE CEPA)",
                description=(
                    "To benefit from preferential duty rates under the India-UAE Comprehensive "
                    "Economic Partnership Agreement (CEPA), exporters must obtain a preferential "
                    "Certificate of Origin in the prescribed Form A or CEPA-specific format, "
                    "issued by authorised agencies in India."
                ),
                category=RequirementCategory.TRADE_DOCUMENTATION,
                applicable_hs_codes=None,
                applicable_country_iso=["ARE"],
                required_document_types=["certificate_of_origin"],
                evidence_fields=["cepa_form", "origin_criterion", "exporter_name"],
                weight=7,
                is_mandatory=False,
                issuing_authority="Export Inspection Council (EIC) / FIEO / Chambers of Commerce",
                source_url="https://www.commerce.gov.in/trade-agreements/india-uae-cepa/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.VERIFIED,
                notes="Optional but required to claim FTA benefits under India-UAE CEPA (in force since May 2022).",
            ),

            # ── Textiles & Garments ───────────────────────────────
            Requirement(
                code="IND-TEXTILE-001",
                name="Textile Committee Quality Certificate",
                description=(
                    "Exporters of textiles and garments may be required to obtain quality "
                    "certificates from the Textile Committee for certain markets. Pre-shipment "
                    "inspection and testing for fibre content, dimensional stability, and "
                    "colour fastness may be required by the importing country."
                ),
                category=RequirementCategory.PRODUCT_QUALITY,
                applicable_hs_codes=["50", "51", "52", "53", "54", "55", "56", "57", "58",
                                      "59", "60", "61", "62", "63"],
                applicable_country_iso=None,
                required_document_types=["quality_certificate", "test_report"],
                evidence_fields=["test_report_number", "parameters_tested"],
                weight=5,
                is_mandatory=False,
                issuing_authority="Textile Committee, Ministry of Textiles, India",
                source_url="https://www.textilecommittee.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.UNVERIFIED,
                notes=(
                    "Mandatory for some markets (e.g., certain EU buyers require OEKO-TEX or "
                    "GOTS certification). Verify current requirements with the buyer."
                ),
            ),

            # ── BIS / Quality ─────────────────────────────────────
            Requirement(
                code="IND-BIS-001",
                name="BIS Certification (where applicable)",
                description=(
                    "Bureau of Indian Standards (BIS) certification is mandatory for certain "
                    "product categories under the compulsory certification scheme. Exporters "
                    "should verify if their product falls under a BIS compulsory standard and "
                    "obtain the ISI Mark or BIS certification accordingly."
                ),
                category=RequirementCategory.PRODUCT_QUALITY,
                applicable_hs_codes=["84", "85", "73", "39", "28", "29"],
                applicable_country_iso=None,
                required_document_types=["bis_certificate"],
                evidence_fields=["bis_licence_number", "standard_number", "validity_date"],
                weight=6,
                is_mandatory=False,
                issuing_authority="Bureau of Indian Standards (BIS)",
                source_url="https://www.bis.gov.in/",
                source_date=datetime.date(2024, 1, 1),
                kb_status=RequirementStatus.UNVERIFIED,
                notes=(
                    "Mandatory only for products under compulsory BIS schemes. "
                    "Check BIS website for current list of mandatory certification products."
                ),
            ),
        ]

        for req in requirements:
            if not db.query(Requirement).filter(Requirement.code == req.code).first():
                db.add(req)

        db.commit()
        print("✓ Seed complete:")
        print(f"  Products:      {db.query(Product).count()}")
        print(f"  Countries:     {db.query(DestinationCountry).count()}")
        print(f"  Requirements:  {db.query(Requirement).count()}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
