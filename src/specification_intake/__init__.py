from .adapters import adapt_docx, adapt_pdf, adapt_specification
from .models import DocumentRole, PairFormat, UnifiedSourceBlock, UnifiedSpecificationDocument
from .pairing import SpecificationPair, build_pair, classify_pair

__all__ = [
    "DocumentRole",
    "PairFormat",
    "SpecificationPair",
    "UnifiedSourceBlock",
    "UnifiedSpecificationDocument",
    "adapt_docx",
    "adapt_pdf",
    "adapt_specification",
    "build_pair",
    "classify_pair",
]
