from .backup import SqliteEntry
from utils import logger
import sqlite3

KEYWORDS = ("uuid", "player", "user", "name", "nick", "owner")

class SQLITEScanner():
    def __init__(self, logger: logger):
        self._logger = logger

    def scan_and_update(self, file_path: str, old_uuid: str, new_uuid: str, old_name: str, new_name: str, dry_run: bool = True) -> int:
        results = []
        with sqlite3.connect(file_path) as conn:
            tables = self._get_tables(conn)
            for table in tables:
                columns = self._get_columns(conn, table)
                interesting = self._analyze_columns(columns)
                for column in interesting:
                    count_uuid = self._update_column(conn, table, column, old_uuid, new_uuid, dry_run)
                    count_name = self._update_column(conn, table, column, old_name, new_name, dry_run)
                    if count_uuid > 0 or count_name > 0:
                        results.append(SqliteEntry(file_path, table, column))
            if not dry_run:
                conn.commit()
        return results

    def _update_column(self, conn: sqlite3.Connection, table: str, column: str, old_value: str, new_value: str, dry_run: bool) -> int:
        cur = conn.cursor()
        try:
            if dry_run:
                cur.execute(
                    f"""
                    SELECT COUNT(*) FROM {self._quote_ident(table)}
                    WHERE {self._quote_ident(column)} = ?
                    """,
                    (old_value,)
                )
                return cur.fetchone()[0]
            try:
                cur.execute(
                    f"""
                    UPDATE {self._quote_ident(table)}
                    SET {self._quote_ident(column)} = ?
                    WHERE {self._quote_ident(column)} = ?
                    """,
                    (new_value, old_value)
                )
            except Exception as e:
                self._logger.error(f"Error updating column '{column}' of table '{table}': {e}")
            return cur.rowcount
        finally:
            cur.close()

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
