"""
ExportIQ — Structured field extraction service.
Extracts business and document identifiers (GSTIN, PAN, IEC, Udyam, dates, names)
from document text using robust regular expressions and rule-based parsing.
"""
import re
from typing import Dict, Any


def extract_fields_from_text(text: str, document_type: str) -> Dict[str, Any]:
    """
    Extract structured fields from document text based on document type and regex patterns.
    """
    fields: Dict[str, Any] = {}
    if not text:
        return fields

    # 1. GSTIN pattern: 2 digits, 5 letters, 4 digits, 1 letter, 1 alphanumeric, Z, 1 alphanumeric
    gstin_match = re.search(r'\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b', text)
    if gstin_match:
        fields['gstin'] = gstin_match.group(1)

    # 2. PAN pattern: 5 letters (4 alpha + 1 entity letter P/C/H/F/A/T/B/L/J/G), 4 digits, 1 letter
    pan_match = re.search(r'\b([A-Z]{3}[ABCFGHLJPTF][A-Z][0-9]{4}[A-Z])\b', text)
    if pan_match:
        fields['pan'] = pan_match.group(1)
    else:
        # Generic fallback for PAN if standard regex doesn't match
        pan_generic = re.search(r'\b(PAN[:\s\-]*)([A-Z]{5}[0-9]{4}[A-Z]{1})\b', text, re.IGNORECASE)
        if pan_generic:
            fields['pan'] = pan_generic.group(2)

    # 3. IEC number: 10 digits in India (DGFT format)
    iec_match = re.search(r'(?:IEC|Importer[\s\-]*Exporter[\s\-]*Code)[:\s\-]*([0-9]{10})\b', text, re.IGNORECASE)
    if iec_match:
        fields['iec_number'] = iec_match.group(1)
    else:
        # Fallback 10-digit number
        ten_digits = re.search(r'\b([0-9]{10})\b', text)
        if ten_digits and document_type == 'iec_certificate':
            fields['iec_number'] = ten_digits.group(1)

    # 4. Udyam Registration number
    udyam_match = re.search(r'\b(UDYAM\-[A-Z]{2}\-[0-9]{2}\-[0-9]{7})\b', text, re.IGNORECASE)
    if udyam_match:
        fields['udyam_number'] = udyam_match.group(1)

    # 5. FSSAI License number (14 digits)
    fssai_match = re.search(r'\b([0-9]{14})\b', text)
    if fssai_match:
        fields['fssai_license_number'] = fssai_match.group(1)

    # 6. Dates (DD/MM/YYYY or YYYY-MM-DD)
    dates = re.findall(r'\b(0[1-9]|[12][0-9]|3[01])[-/.](0[1-9]|1[012])[-/.](19|20)[0-9]{2}\b', text)
    if dates:
        fields['dates_found'] = ['/'.join(d[:3]) for d in dates[:5]]

    return fields
