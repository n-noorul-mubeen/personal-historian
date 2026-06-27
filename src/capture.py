import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _generate_id(timestamp: datetime) -> str:
    return timestamp.strftime("%Y%m%dT%H%M%S")


def capture_entry(text: Optional[str] = None, root_dir: Optional[Path | str] = None, timestamp: Optional[str] = None) -> Path:
    root = Path(root_dir or Path(__file__).resolve().parent.parent)
    journal_dir = root / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)

    if text is None:
        text = sys.stdin.read()

    if timestamp is None:
        created_at = datetime.now(timezone.utc)
    else:
        created_at = datetime.fromisoformat(timestamp)

    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    path = journal_dir / created_at.strftime("%Y/%m")
    path.mkdir(parents=True, exist_ok=True)

    filename = created_at.strftime("%Y-%m-%d_%H%M%S.md")
    entry_path = path / filename
    entry_content = (
        "---\n"
        f"schema_version: 1\n"
        f"id: {_generate_id(created_at)}\n"
        f"created_at: {created_at.isoformat()}\n"
        "---\n"
        f"{text}"
    )
    entry_path.write_text(entry_content, encoding="utf-8")
    return entry_path


if __name__ == "__main__":
    capture_entry()
