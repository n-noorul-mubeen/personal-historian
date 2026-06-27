import hashlib
import tempfile
import unittest
from pathlib import Path

from src.capture import capture_entry
from src.database import get_connection
from src.export import export_entries
from src.indexer import index_journal


class HistorianWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory(dir="/tmp", prefix="historian-test-")
        self.root = Path(self.temp_dir.name)
        self.journal_dir = self.root / "journal"
        self.journal_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_capture_and_index_flow(self) -> None:
        entry_path = capture_entry("hello historian", root_dir=self.root, timestamp="2024-01-02T03:04:05+00:00")
        self.assertTrue(entry_path.exists())
        content = entry_path.read_text(encoding="utf-8")
        self.assertIn("schema_version: 1", content)
        self.assertIn("hello historian", content)

        db_path = self.root / "historian.db"
        index_journal(root_dir=self.root, db_path=db_path)

        conn = get_connection(db_path=db_path)
        try:
            row = conn.execute(
                "SELECT filepath, content_hash FROM entries WHERE filepath = ?",
                (entry_path.relative_to(self.root).as_posix(),),
            ).fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[1], self._hash_file(entry_path))

            fts_row = conn.execute(
                "SELECT entry_id FROM entries_fts WHERE entries_fts MATCH ?",
                ("historian",),
            ).fetchone()
            self.assertIsNotNone(fts_row)
        finally:
            conn.close()

    def test_export_groups_entries_chronologically(self) -> None:
        first = capture_entry("first", root_dir=self.root, timestamp="2024-01-02T03:04:05+00:00")
        second = capture_entry("second", root_dir=self.root, timestamp="2024-01-03T03:04:05+00:00")

        output_path = self.root / "all_entries.md"
        export_entries(root_dir=self.root, output_path=output_path)

        exported = output_path.read_text(encoding="utf-8")
        self.assertIn("first", exported)
        self.assertIn("second", exported)
        self.assertLess(exported.index("first"), exported.index("second"))

    def _hash_file(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
