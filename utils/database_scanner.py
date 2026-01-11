from .backup import MySQLEntry
from utils import logger
from tqdm import tqdm

try:
    import mysql.connector
    from mysql.connector import MySQLConnection
except ImportError:
    logger.warn("Mysql not avaible, install it with pip install mysql")

KEYWORDS = ("uuid", "player", "user", "name", "nick", "owner")
SYSTEM_DATABASES = {
    "information_schema",
    "mysql",
    "performance_schema",
    "sys"
}

class MySQLScanner:
    def __init__(self, logger: logger, host: str, port: int, user: str, password: str):
        self._logger = logger
        self._config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
        }

    def scan_all_databases(self, old_uuid: str, old_name: str) -> list["MySQLEntry"]:
        results = []
        conn = mysql.connector.connect(**self._config)
        try:
            databases = self._get_databases(conn)
            for db in tqdm(databases, desc="Scanning databases"):
                if db in SYSTEM_DATABASES:
                    continue
                results.extend(self._scan_database(conn, db, old_uuid, old_name))
        finally:
            conn.close()
        return results

    def update_entries(
        self,
        entries: list["MySQLEntry"],
        old_uuid: str,
        new_uuid: str,
        old_name: str,
        new_name: str,
        dry_run: bool = False
    ) -> int:
        total_updated = 0
        conn = mysql.connector.connect(**self._config)

        try:
            cur = conn.cursor()
            for entry in tqdm(entries, desc="Updating MySQL entries"):
                conn.database = entry.database

                total_updated += self._update_value(
                    cur,
                    entry.table,
                    entry.column,
                    old_uuid,
                    new_uuid,
                    dry_run
                )

                total_updated += self._update_value(
                    cur,
                    entry.table,
                    entry.column,
                    old_name,
                    new_name,
                    dry_run
                )

            try:
                if not dry_run:
                    conn.commit()
            except Exception:
                if not dry_run:
                    conn.rollback()
                raise
        finally:
            cur.close()
            conn.close()

        return total_updated

    def _update_value(
        self,
        cur,
        table: str,
        column: str,
        old_value: str,
        new_value: str,
        dry_run: bool
    ) -> int:
        query = f"""
            UPDATE `{table}`
            SET `{column}` = %s
            WHERE `{column}` = %s
        """

        if dry_run:
            cur.execute(
                f"SELECT COUNT(*) FROM `{table}` WHERE `{column}` = %s",
                (old_value,)
            )
            return cur.fetchone()[0]

        cur.execute(query, (new_value, old_value))
        return cur.rowcount

    def _get_databases(self, conn: MySQLConnection) -> list[str]:
        cur = conn.cursor()
        try:
            cur.execute("SHOW DATABASES")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()

    def _scan_database(self, conn: MySQLConnection, database: str, old_uuid: str, old_name: str) -> list["MySQLEntry"]:
        results = []
        conn.database = database
        tables = self._get_tables(conn)
        for table in tqdm(tables, desc=f"Scanning tables in {database}", leave=False):
            columns = self._get_columns(conn, table)
            interesting = self._analyze_columns(columns)
            for column in interesting:
                if self._search_column(conn, table, column, old_uuid, old_name) > 0:
                    results.append(MySQLEntry(database, table, column))
        return results

    def _get_tables(self, conn: MySQLConnection) -> list[str]:
        cur = conn.cursor()
        try:
            cur.execute("SHOW TABLES")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()

    def _get_columns(self, conn: MySQLConnection, table_name: str) -> list[str]:
        cur = conn.cursor()
        try:
            cur.execute(f"SHOW COLUMNS FROM `{table_name}`")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()

    @staticmethod
    def _analyze_columns(columns: list[str]) -> list[str]:
        return [c for c in columns if any(k in c.lower() for k in KEYWORDS)]

    def _search_column(self, conn: MySQLConnection, table: str, column: str, old_uuid: str, old_name: str) -> int:
        cur = conn.cursor()
        try:
            query = f"""
                SELECT COUNT(*) FROM `{table}`
                WHERE `{column}` = %s OR `{column}` = %s
            """
            cur.execute(query, (old_uuid, old_name))
            return cur.fetchone()[0]
        finally:
            cur.close()
