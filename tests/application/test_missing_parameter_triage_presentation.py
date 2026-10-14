from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class MissingParameterTriagePresentationTests(unittest.TestCase):
    def test_missing_fields_have_provisional_entry_without_feasibility_promotion(self):
        source = (ROOT / "pages" / "09_Data_Upload.py").read_text(encoding="utf-8")
        self.assertIn('def render_missing_field_triage(rows, pair)', source)
        self.assertIn('row["Comparison Status"] == "Incomplete"', source)
        self.assertIn('for role in ("Existing", "Proposed"):', source)
        self.assertIn('render_missing_field_triage(rows, pair)', source)
        self.assertIn("NOT used by", source)
        self.assertIn("canonical mapping or feasibility", source)
        self.assertIn("Unverified entry only.", source)


if __name__ == "__main__":
    unittest.main()
