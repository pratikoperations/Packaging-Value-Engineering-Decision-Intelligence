from __future__ import annotations

import unittest
from pathlib import Path

from app import _task_page


class TaskNavigationTests(unittest.TestCase):
    def test_required_task_pages_register_exactly_once(self):
        filenames = [
            "01_Project_Dashboard.py",
            "02_Upload_Validate.py",
            "04_Business_Thresholds.py",
            "05_Controlled_Scenarios.py",
            "06_Decision_History.py",
            "07_PVE_2_0_AI_Word_Intake.py",
            "08_PVE_2_1_Digital_PDF_Intake.py",
            "09_Data_Upload.py",
            "03_PVE_1_1_Guided_Workflow.py",
        ]
        registrations = [result for name in filenames if (result := _task_page(Path(name))) is not None]
        titles = [title for _, title in registrations]
        self.assertEqual(
            titles,
            [
                "Project Dashboard",
                "Business Rules & Thresholds",
                "Scenario Analysis",
                "Decision Records",
                "Data Upload",
                "Guided Workflow",
            ],
        )
        self.assertEqual(len(titles), len(set(titles)))

    def test_legacy_upload_word_and_pdf_pages_are_not_registered(self):
        for filename in (
            "02_Upload_Validate.py",
            "07_PVE_2_0_AI_Word_Intake.py",
            "08_PVE_2_1_Digital_PDF_Intake.py",
        ):
            self.assertIsNone(_task_page(Path(filename)))


if __name__ == "__main__":
    unittest.main()
