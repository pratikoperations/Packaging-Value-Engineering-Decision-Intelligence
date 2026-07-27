from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDED_PAGE = ROOT / "pages" / "03_PVE_1_1_Guided_Workflow.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GuidedTraceabilityPresentationTests(unittest.TestCase):
    def test_guided_page_does_not_render_raw_json(self) -> None:
        source = GUIDED_PAGE.read_text(encoding="utf-8")
        self.assertNotIn("st.json(", source)
        self.assertIn(
            "No additional source references are recorded for this synthetic demonstration dataset.",
            source,
        )

    def test_empty_traceability_returns_no_rows(self) -> None:
        module = load_module(GUIDED_PAGE, "pve_guided_traceability_empty")
        self.assertEqual(module.source_traceability_rows({}), [])

    def test_traceability_is_flattened_for_table_display(self) -> None:
        module = load_module(GUIDED_PAGE, "pve_guided_traceability_rows")
        rows = module.source_traceability_rows(
            {
                "dataset": {
                    "source_type": "canonical_json",
                    "validated": True,
                }
            }
        )
        values = {row["Source reference"]: row["Recorded value"] for row in rows}
        self.assertEqual(values["Dataset — Source Type"], "canonical json")
        self.assertEqual(values["Dataset — Validated"], "Yes")


if __name__ == "__main__":
    unittest.main()
