# Personal Historian

Personal Historian is a local-first journaling tool for capturing plain-text entries and searching them with SQLite FTS5.

It keeps your journal as simple Markdown files on disk, while using a rebuildable SQLite index so you can search quickly without relying on a cloud service.

## Why it exists

- Keep your entries as plain text files you can edit and back up freely
- Search locally with SQLite FTS5
- Work entirely offline
- Stay simple: no accounts, no syncing, no hidden backend

## Features

- Create timestamped journal entries from standard input
- Rebuild or refresh the search index from your journal files
- Browse and search entries in a lightweight text-based UI
- Export all entries into a single Markdown file

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

## Project layout

- journal/ — your Markdown journal files, organized by year and month
- historian.db — the SQLite database used for search indexing
- src/capture.py — creates new journal entries from stdin
- src/indexer.py — scans journal files and rebuilds the search index
- src/app.py — the interactive search and browsing interface
- src/export.py — combines all journal entries into one export file

## How it works

1. The capture command writes a Markdown entry with YAML frontmatter.
2. The indexer scans the journal directory and updates the SQLite FTS5 index.
3. The app queries that index so you can search and browse entries quickly.
4. The export command writes all entries into a single Markdown document.

## Notes

- The Markdown files in the journal directory are the source of truth.
- The SQLite database is disposable and can be rebuilt at any time.
- The project is intentionally minimal and local-first.
