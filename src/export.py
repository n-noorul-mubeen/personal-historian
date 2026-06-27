from pathlib import Path
from typing import Optional


def export_entries(root_dir: Optional[Path | str] = None, output_path: Optional[Path | str] = None) -> Path:
    root = Path(root_dir or Path(__file__).resolve().parent.parent)
    journal_dir = root / "journal"
    output = Path(output_path or root / "all_entries.md")

    entries = sorted(journal_dir.rglob("*.md"))
    content = []
    for entry_path in entries:
        if entry_path.is_file():
            content.append(entry_path.read_text(encoding="utf-8"))
    output.write_text("\n\n".join(content), encoding="utf-8")
    return output
