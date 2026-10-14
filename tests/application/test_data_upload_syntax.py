from __future__ import annotations

import ast
import unittest
from pathlib import Path


class DataUploadSyntaxTests(unittest.TestCase):
    def test_streamlit_upload_page_compiles(self):
        page = Path(__file__).resolve().parents[2] / "pages" / "09_Data_Upload.py"
        source = page.read_text(encoding="utf-8")
        ast.parse(source, filename=str(page))
        compile(source, str(page), "exec")


if __name__ == "__main__":
    unittest.main()
