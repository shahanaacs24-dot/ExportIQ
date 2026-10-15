"""
ExportIQ — OCR extraction service using pytesseract / Pillow.
Extracts text from images (PNG, JPG, TIFF) or scanned PDF pages.
"""
import logging
import os
from PIL import Image

logger = logging.getLogger(__name__)


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image file using pytesseract.
    Returns empty string if Tesseract is not installed or extraction fails.
    """
    try:
        import pytesseract
        # Check if tesseract binary is available
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip() if text else ""
    except Exception as e:
        logger.warning(f"OCR extraction unavailable or failed for {image_path}: {e}")
        return ""
