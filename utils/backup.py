from dataclasses import dataclass
from utils import logger
import os
import json
from datetime import datetime

@dataclass
class SqliteEntry:
    path: str
    table: str
    column: str

@dataclass
class MySQLEntry:
    database: str
    table: str
    column: str

class Backupper:
    def __init__(self, logger: logger, backup_path: str):
        self._logger = logger
        self._backup_path = backup_path

    def log_changes(self, items: list, log_name: str = None):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = log_name or f"changes-{timestamp}.json"
        log_path = os.path.join(self._backup_path, log_file)
        os.makedirs(self._backup_path, exist_ok=True)

        json_items = []

        for item in items:
            if isinstance(item, MySQLEntry):
                json_items.append({
                    "type": "db",
                    "database": item.database,
                    "table": item.table,
                    "column": item.column
                })
            elif isinstance(item, SqliteEntry):
                json_items.append({
                    "type": "sqlite",
                    "path": item.path,
                    "table": item.table,
                    "column": item.column
                })
            elif isinstance(item, dict) and "type" in item and "path" in item:
                json_items.append(item)
            else:
                self._logger.warn(f"Unknown item type for logging: {item}")

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(json_items, f, indent=4)

        self._logger.info(f"Backup saved in {log_path}")
        return log_path

    @staticmethod
    def make_rename(path: str):
        return {"type": "rename", "path": path}

    @staticmethod
    def make_edited(path: str):
        return {"type": "edited", "path": path}
