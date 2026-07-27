from __future__ import annotations

import io
import unittest
import zipfile

from src.document_intake import (
    DocumentRole,
    DocumentValidationError,
    SourceBlockType,
    parse_document_pair,
    parse_validated_docx,
    validate_document_pair,
    validate_docx,
)

CONTENT_TYPES = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''


def make_docx(*, heading="Specification", paragraph="Item ABC", table_value="RSC", extra_parts=None):
    document_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>{heading}</w:t></w:r></w:p>
    <w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Box style</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>{table_value}</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
  </w:body>
</w:document>'''.encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("word/document.xml", document_xml)
        for name, content in (extra_parts or {}).items():
            archive.writestr(name, content)
    return buffer.getvalue()


class DocxValidationTests(unittest.TestCase):
    def test_accepts_normal_docx_and_computes_hash(self):
        content = make_docx()
        validated = validate_docx("existing.DOCX", content, DocumentRole.EXISTING)
        self.assertEqual(validated.filename, "existing.DOCX")
        self.assertEqual(len(validated.sha256), 64)
        self.assertIn("word/document.xml", validated.part_names)

    def test_rejects_wrong_extension_empty_and_invalid_zip(self):
        with self.assertRaises(DocumentValidationError):
            validate_docx("existing.pdf", b"x", DocumentRole.EXISTING)
        with self.assertRaises(DocumentValidationError):
            validate_docx("existing.docx", b"", DocumentRole.EXISTING)
        with self.assertRaises(DocumentValidationError):
            validate_docx("existing.docx", b"not-a-zip", DocumentRole.EXISTING)

    def test_rejects_missing_required_part(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        with self.assertRaisesRegex(DocumentValidationError, "word/document.xml"):
            validate_docx("existing.docx", buffer.getvalue(), DocumentRole.EXISTING)

    def test_pair_requires_exact_roles_and_rejects_duplicates(self):
        content = make_docx()
        existing = validate_docx("a.docx", content, DocumentRole.EXISTING)
        proposed_same = validate_docx("b.docx", content, DocumentRole.PROPOSED)
        with self.assertRaisesRegex(DocumentValidationError, "duplicates"):
            validate_document_pair((existing, proposed_same))

        proposed = validate_docx("b.docx", make_docx(table_value="B flute"), DocumentRole.PROPOSED)
        resolved_existing, resolved_proposed = validate_document_pair((proposed, existing))
        self.assertEqual(resolved_existing.role, DocumentRole.EXISTING)
        self.assertEqual(resolved_proposed.role, DocumentRole.PROPOSED)

        duplicate_role = validate_docx("c.docx", make_docx(paragraph="Other"), DocumentRole.EXISTING)
        with self.assertRaisesRegex(DocumentValidationError, "one existing and one proposed"):
            validate_document_pair((existing, duplicate_role))


class DocxParserTests(unittest.TestCase):
    def test_extracts_heading_paragraph_and_table_cells_in_order(self):
        validated = validate_docx("existing.docx", make_docx(), DocumentRole.EXISTING)
        parsed = parse_validated_docx(validated)
        self.assertEqual(
            [block.block_type for block in parsed.blocks],
            [
                SourceBlockType.HEADING,
                SourceBlockType.PARAGRAPH,
                SourceBlockType.TABLE_CELL,
                SourceBlockType.TABLE_CELL,
            ],
        )
        self.assertEqual([block.text for block in parsed.blocks], ["Specification", "Item ABC", "Box style", "RSC"])
        self.assertTrue(all(block.location.section_title == "Specification" for block in parsed.blocks))
        self.assertEqual(parsed.table_cells[1].location.table_index, 0)
        self.assertEqual(parsed.table_cells[1].location.row_index, 0)
        self.assertEqual(parsed.table_cells[1].location.cell_index, 1)

    def test_source_ids_are_stable_and_change_with_document(self):
        content = make_docx()
        first = parse_validated_docx(validate_docx("a.docx", content, DocumentRole.EXISTING))
        second = parse_validated_docx(validate_docx("renamed.docx", content, DocumentRole.EXISTING))
        changed = parse_validated_docx(
            validate_docx("a.docx", make_docx(paragraph="Changed"), DocumentRole.EXISTING)
        )
        self.assertEqual([b.block_id for b in first.blocks], [b.block_id for b in second.blocks])
        self.assertNotEqual(first.blocks[0].block_id, changed.blocks[0].block_id)
        self.assertEqual(len({b.block_id for b in first.blocks}), len(first.blocks))

    def test_detects_unsupported_images_embeddings_and_macros_without_execution(self):
        content = make_docx(
            extra_parts={
                "word/media/image1.png": b"image",
                "word/embeddings/object1.bin": b"object",
                "word/vbaProject.bin": b"macro",
            }
        )
        parsed = parse_validated_docx(validate_docx("a.docx", content, DocumentRole.EXISTING))
        self.assertEqual(
            {item.code for item in parsed.unsupported_content},
            {"image_content", "embedded_object", "macro_content"},
        )

    def test_rejects_malformed_document_xml(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("[Content_Types].xml", CONTENT_TYPES)
            archive.writestr("word/document.xml", b"<broken")
        validated = validate_docx("bad.docx", buffer.getvalue(), DocumentRole.EXISTING)
        with self.assertRaisesRegex(DocumentValidationError, "malformed"):
            parse_validated_docx(validated)

    def test_public_pair_api_returns_exact_roles(self):
        pair = parse_document_pair(
            "existing.docx",
            make_docx(table_value="BC flute"),
            "proposed.docx",
            make_docx(table_value="B flute"),
        )
        self.assertEqual(pair.existing.role, DocumentRole.EXISTING)
        self.assertEqual(pair.proposed.role, DocumentRole.PROPOSED)
        self.assertEqual(pair.existing.table_cells[-1].text, "BC flute")
        self.assertEqual(pair.proposed.table_cells[-1].text, "B flute")


if __name__ == "__main__":
    unittest.main()
