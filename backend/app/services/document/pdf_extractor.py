"""
ExportIQ — PDF text extraction using pdfminer.six.
Handles native (text-based) PDFs. For scanned PDFs, returns empty text
so the caller can fall back to OCR.
"""
import io
import logging
from pathlib import Path

from pdfminer.high_level import extract_text as pdfminer_extract
from pdfminer.pdfparser import PDFSyntaxError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> tuple[str, bool]:
    """
    Extract text from a PDF file using pdfminer.six.

    Returns (text, is_scanned) where:
    - text: extracted text string (may be empty for scanned-only PDFs)
    - is_scanned: True if the PDF appears to be an image-only (scanned) PDF
    """
    try:
        text = pdfminer_extract(file_path)
        cleaned = text.strip() if text else ""
        # Heuristic: if fewer than 50 characters extracted from a PDF,
        # it is likely scanned (image-only) and needs OCR.
        is_scanned = len(cleaned) < 50
        return cleaned, is_scanned
    except PDFSyntaxError as e:
        logger.warning(f"PDF syntax error for {file_path}: {e}")
        return "", True
    except Exception as e:
        logger.error(f"pdfminer extraction failed for {file_path}: {e}")
        return "", True
