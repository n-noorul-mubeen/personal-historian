# Personal Historian

A local-first journal for capturing plain-text entries and searching them with SQLite FTS5.

## Quick start

1. Create an entry:
   ```bash
   python -m src.capture <<'EOF'
   Today I wrote a note.
   EOF
   ```
2. Rebuild the search index:
   ```bash
   python -m src.indexer
   ```
3. Launch the TUI:
   ```bash
   python -m src.app
   ```
4. Export everything:
   ```bash
   python -m src.export
   ```
