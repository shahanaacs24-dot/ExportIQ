"""
ExportIQ — Document processing unit and integration tests.
"""
import os
import io
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.document.field_extractor import extract_fields_from_text
from app.services.document.pdf_extractor import extract_text_from_pdf

client = TestClient(app)


def test_field_extractor():
    sample_text = (
        "GOVERNMENT OF INDIA\n"
        "MINISTRY OF COMMERCE AND INDUSTRY\n"
        "DIRECTORATE GENERAL OF FOREIGN TRADE\n"
        "Importer Exporter Code (IEC): 0388002931\n"
        "GSTIN: 27AAAAA0000A1Z5\n"
        "PAN: ABCDE1234F\n"
        "Date of Issue: 15/01/2023\n"
    )
    fields = extract_fields_from_text(sample_text, "iec_certificate")
    assert fields.get("gstin") == "27AAAAA0000A1Z5"
    assert fields.get("pan") == "ABCDE1234F"
    assert fields.get("iec_number") == "0388002931"


def test_pdf_extractor_nonexistent():
    text, is_scanned = extract_text_from_pdf("nonexistent_file.pdf")
    assert text == ""
    assert is_scanned is True
