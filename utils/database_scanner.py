from dataclasses import dataclass
from utils import logger

try:
    import mysql.connector
    from mysql.connector import MySQLConnection
except:
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

    def scan_all_databases(self, old_uuid: str, old_name: str) -> list["DBEntry"]:
        results = []
        conn = mysql.connector.connect(**self._config)
        try:
            databases = self._get_databases(conn)
            for db in databases:
                if db in SYSTEM_DATABASES:
                    continue
                results.extend(self._scan_database(conn, db, old_uuid, old_name))
        finally:
            conn.close()
        return results

    def _get_databases(self, conn: MySQLConnection) -> list[str]:
        cur = conn.cursor()
        try:
            cur.execute("SHOW DATABASES")
            return [row[0] for row in cur.fetchall()]
        finally:
            cur.close()

    def _scan_database(self, conn: MySQLConnection, database: str, old_uuid: str, old_name: str) -> list["DBEntry"]:
        results = []
        conn.database = database
        tables = self._get_tables(conn)
        for table in tables:
            columns = self._get_columns(conn, table)
            interesting = self._analyze_columns(columns)
            for column in interesting:
                if self._search_column(conn, table, column, old_uuid, old_name) > 0:
                    results.append(DBEntry(database, table, column))
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

@dataclass
class DBEntry:
    database: str
    table: str
    column: str
