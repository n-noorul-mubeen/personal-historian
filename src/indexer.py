import hashlib
from pathlib import Path
from typing import Optional

from src.database import get_connection


def _read_frontmatter_and_content(path: Path) -> tuple[Optional[dict[str, str]], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None, text

    parts = text.split("\n---\n", 1)
    if len(parts) != 2:
        return None, text

    frontmatter_lines = parts[0].splitlines()[1:]
    metadata: dict[str, str] = {}
    for line in frontmatter_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, parts[1]


def _hash_content(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def index_journal(root_dir: Optional[Path | str] = None, db_path: Optional[Path | str] = None) -> None:
    root = Path(root_dir or Path(__file__).resolve().parent.parent)
    db = Path(db_path or root / "historian.db")
    journal_dir = root / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    conn = get_connection(db_path=db)
    try:
        existing_files = {row["filepath"] for row in conn.execute("SELECT filepath FROM entries").fetchall()}
        journal_files = []
        for path in sorted(journal_dir.rglob("*.md")):
            if not path.is_file():
                continue
            journal_files.append(path.relative_to(root).as_posix())

        for path in sorted(journal_dir.rglob("*.md")):
            if not path.is_file():
                continue
            metadata, content = _read_frontmatter_and_content(path)
            timestamp = (metadata or {}).get("created_at") or path.stem
            content_hash = _hash_content(path)
            rel_path = path.relative_to(root).as_posix()

            conn.execute(
                "INSERT INTO entries (filepath, timestamp, content_hash) VALUES (?, ?, ?) "
                "ON CONFLICT(filepath) DO UPDATE SET timestamp = excluded.timestamp, content_hash = excluded.content_hash",
                (rel_path, timestamp, content_hash),
            )
            entry_row = conn.execute("SELECT id FROM entries WHERE filepath = ?", (rel_path,)).fetchone()
            if entry_row is None:
                continue
            entry_id = entry_row[0]
            conn.execute("DELETE FROM entries_fts WHERE entry_id = ?", (entry_id,))
            conn.execute(
                "INSERT INTO entries_fts (entry_id, content) VALUES (?, ?)",
                (entry_id, content),
            )

        for stale_path in existing_files - set(journal_files):
            stale_row = conn.execute("SELECT id FROM entries WHERE filepath = ?", (stale_path,)).fetchone()
            if stale_row is None:
                continue
            conn.execute("DELETE FROM entries_fts WHERE entry_id = ?", (stale_row[0],))
            conn.execute("DELETE FROM entries WHERE id = ?", (stale_row[0],))

        conn.commit()
    finally:
        conn.close()
