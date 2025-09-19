# analyses/services/ocr.py
from __future__ import annotations
from typing import List, Dict, Tuple
import io
import re
import os
from datetime import datetime

from PIL import Image
import pytesseract
from pdf2image import convert_from_path

from analyses.models import AnalysisResult, Analysis

DATE_RE = re.compile(r"\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b")
# Example line formats:
# Hemoglobin: 13.5 g/dL (12-16)
# Glucose  98 mg/dL  (70 - 110)
LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9 _\-/()%]+?)\s*[:\-]?\s+(?P<val>[<>]?\s*\d+[.,]?\d*)?\s*(?P<unit>[A-Za-z/%µμ]+(?:\/[A-Za-z]+)?)?\s*(?:\((?P<ref>[^)]+)\))?\s*$"
)


def _pil_images_from_file(filepath: str) -> List[Image.Image]:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in {".pdf"}:
        return convert_from_path(filepath)  # list of PIL images
    # images (png/jpg/jpeg etc.)
    img = Image.open(filepath)
    return [img]


def _ocr_images(images: List[Image.Image], lang: str = "eng") -> str:
    texts: List[str] = []
    for i, page in enumerate(images, start=1):
        # Basic preproc (grayscale)
        gray = page.convert("L")
        txt = pytesseract.image_to_string(gray, lang=lang)
        texts.append(f"--- PAGE {i} ---\n{txt}")
    return "\n".join(texts).strip()


def _parse_report_date(text: str) -> datetime | None:
    m = DATE_RE.search(text)
    if not m:
        return None
    raw = m.group(1).replace(".", "-").replace("/", "-")
    # Try a few common formats
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m-%d-%Y", "%d-%m-%y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def _extract_results(text: str) -> List[Dict[str, str]]:
    results: List[Dict[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        name = (m.group("name") or "").strip().rstrip(":")
        val = (m.group("val") or "").strip()
        unit = (m.group("unit") or "").strip()
        ref = (m.group("ref") or "").strip()
        # tiny sanity filters
        if len(name) < 2:
            continue
        if not any([val, unit, ref]):
            continue
        results.append(
            {
                "test_name": name,
                "value": val,
                "unit": unit,
                "reference_range": ref,
            }
        )
    return results


def run_ocr_and_extract(analysis: Analysis, lang: str = "eng") -> Tuple[str, List[Dict[str, str]], datetime | None]:
    """
    Returns: (full_text, rows, report_date)
    """
    images = _pil_images_from_file(analysis.file.path)
    text = _ocr_images(images, lang=lang)
    rows = _extract_results(text)
    report_dt = _parse_report_date(text)
    return text, rows, report_dt


def save_ocr_output(analysis: Analysis, lang: str = "eng") -> None:
    """
    Mutates and saves `analysis` (ocr_text, report_date) and creates AnalysisResult rows.
    """
    full_text, rows, report_dt = run_ocr_and_extract(analysis, lang)
    analysis.ocr_text = full_text
    if report_dt:
        analysis.report_date = report_dt.date()
    analysis.save(update_fields=["ocr_text", "report_date", "date_last_updated"])

    if rows:
        bulk = [
            AnalysisResult(
                analysis=analysis,
                test_name=r["test_name"],
                value=r.get("value"),
                unit=r.get("unit"),
                reference_range=r.get("reference_range"),
            )
            for r in rows
        ]
        AnalysisResult.objects.bulk_create(bulk)
