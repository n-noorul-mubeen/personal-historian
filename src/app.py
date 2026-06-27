from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, ListItem, ListView, Static

from src.database import get_connection
from src.indexer import index_journal


class HistorianApp(App):
    CSS = """
    Screen { layout: vertical; }
    #search { height: 3; }
    #timeline { width: 40%; }
    #reader { width: 60%; }
    """

    def __init__(self, root_dir: Optional[Path | str] = None) -> None:
        super().__init__()
        self.root_dir = Path(root_dir or Path(__file__).resolve().parent.parent)
        self.entry_paths: list[str] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search entries", id="search")
        with Horizontal():
            yield ListView(id="timeline")
            yield Static(id="reader")

    def on_mount(self) -> None:
        index_journal(root_dir=self.root_dir)
        self.refresh_entries()

    def refresh_entries(self, query: str = "") -> None:
        conn = get_connection(db_path=self.root_dir / "historian.db")
        try:
            timeline = self.query_one("#timeline", ListView)
            timeline.clear()
            self.entry_paths = []

            query_text = query.strip()
            if query_text:
                rows = conn.execute(
                    "SELECT e.filepath, e.timestamp FROM entries AS e "
                    "JOIN entries_fts AS f ON e.id = f.entry_id "
                    "WHERE f.content MATCH ? "
                    "ORDER BY e.timestamp DESC",
                    (query_text,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT filepath, timestamp FROM entries ORDER BY timestamp DESC"
                ).fetchall()

            for row in rows:
                self.entry_paths.append(row["filepath"])
                timeline.append(ListItem(Static(row["filepath"])))
        finally:
            conn.close()

    def on_input_changed(self, event: Input) -> None:
        if event.input.id == "search":
            self.refresh_entries(event.value)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if 0 <= event.index < len(self.entry_paths):
            entry_path = self.root_dir / self.entry_paths[event.index]
            if entry_path.exists():
                content = entry_path.read_text(encoding="utf-8")
            else:
                content = "Entry not found."
            self.query_one("#reader", Static).update(content)


if __name__ == "__main__":
    HistorianApp().run()
