# Personal Historian V0.1

## Overview

Personal Historian is a local-first journaling application that stores plain Markdown files as the source of truth and uses SQLite with FTS5 as a rebuildable search index.

## Architecture

- journal/: directory for Markdown entry files stored under YYYY/MM/
- schema.sql: SQLite schema with entries and entries_fts
- src/database.py: creates and initializes the SQLite connection
- src/indexer.py: scans journal files and rebuilds or updates the index
- src/capture.py: captures stdin input into a timestamped Markdown entry
- src/app.py: minimal Textual TUI for searching and browsing entries
- src/export.py: concatenates entries into all_entries.md

## Runtime Flow

1. Capture CLI writes a Markdown file with YAML frontmatter.
2. Indexer reads all journal files and updates the SQLite cache.
3. Textual app queries the FTS5 index and renders matching entries.
4. Export script concatenates the journal files in chronological order.

## Notes

- The Markdown files on disk are authoritative.
- The SQLite database is disposable and rebuildable.
- No AI, embeddings, tagging, or entity extraction are included.
