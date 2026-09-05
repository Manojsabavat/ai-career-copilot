try:
    import pymupdf
except ImportError:  # compatibility with older environments
    import fitz as pymupdf


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF resume."""
    document = pymupdf.open(stream=file_bytes, filetype="pdf")
    try:
        return "\n".join(page.get_text() for page in document).strip()
    finally:
        document.close()
