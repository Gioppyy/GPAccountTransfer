from .backup import SqliteEntry
from utils import logger
import sqlite3

KEYWORDS = ("uuid", "player", "user", "name", "nick", "owner")

class SQLITEScanner():
    def __init__(self, logger: logger):
        self._logger = logger

    def scan(self, file_path: str, old_uuid: str, old_name: str) -> list["SqliteEntry"]:
        with sqlite3.connect(f"file:{file_path}?mode=ro", uri=True) as conn:
            tables = self._get_tables(conn)
            results = []
            for table in tables:
                columns = self._get_columns(conn, table)
                interesting = self._analyze_columns(columns)

                for column in interesting:
                    if self._search_column(conn, table, column, old_uuid, old_name) > 0:
                        results.append(SqliteEntry(file_path, table, column))
            return results

    def _get_tables(self, conn: sqlite3.Connection) -> list[str]:
        with conn:
            cur = conn.cursor()
            try:
                cur.execute("""
                    SELECT name FROM sqlite_master
                    WHERE type='table'
                """)
                return [row[0] for row in cur.fetchall()]
            finally:
                cur.close()
        return []

    def _get_columns(self, conn: sqlite3.Connection, table_name: str) -> list[str]:
        with conn:
            cur = conn.cursor()
            try:
                cur.execute(f"PRAGMA table_info('{table_name}')")
                return [row[1] for row in cur.fetchall()]
            finally:
                cur.close()

    def _analyze_columns(self, columns: list[str]) -> list[str]:
        return [
            c for c in columns
            if any(k in c.lower() for k in KEYWORDS)
        ]

    def _search_column(
        self,
        conn: sqlite3.Connection,
        table: str,
        column: str,
        old_uuid: str,
        old_name: str
    ) -> int:
        cur = conn.cursor()
        try:
            cur.execute(
                f"""
                SELECT COUNT(*) FROM {self._quote_ident(table)}
                WHERE {self._quote_ident(column)} = ?
                OR {self._quote_ident(column)} = ?
                """,
                (old_uuid, old_name)
            )
            return cur.fetchone()[0]
        finally:
            cur.close()

    def _quote_ident(self, name: str) -> str:
        return '"' + name.replace('"', '""') + '"'
