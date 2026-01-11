from .sqlite_scanner import SQLITEScanner
from utils import logger
import json
import os

try:
    import nbtlib
    NBT_AVAILABLE = True
except ImportError:
    NBT_AVAILABLE = False
    logger.warn("nbtlib not installed: NBT files will not be parsed")

class FolderScanner:
    def __init__(self, logger: logger, server_path: str, old_uuid: str, old_name: str):
        self._db_scanner = SQLITEScanner(logger)
        self._server_path = server_path
        self._old_uuid = old_uuid
        self._old_name = old_name
        self._logger = logger
        self._results = []

    def scan(self):
        self._logger.info(f"Searching for any entry")

        for dirpath, _, filenames in os.walk(self._server_path):
            for suffix in [self._old_uuid, self._old_name]:
                for ext in [".dat", ".json"]:
                    fname = f"{suffix}{ext}"
                    if fname in filenames:
                        method = self._process_dat_file if ext == ".dat" else self._process_json_file
                        method(os.path.join(dirpath, fname))

            db_res = []
            for filename in filenames:
                if filename.endswith(".db") or filename.endswith(".sqlite"):
                    db_res.extend(self._db_scanner.scan(os.path.join(dirpath, filename), self._old_uuid, self._old_name))
            self._results.extend(db_res)

        if not self._results:
            self._logger.warn("No entry found UUID")
        else:
            self._logger.info(f"Found {len(self._results)} entry in folders for old name / uuid")

    def _process_dat_file(self, file_path: str) -> None:
        info = {}
        if NBT_AVAILABLE:
            try:
                nbt_data = nbtlib.load(file_path)
                root = nbt_data.get("")
                if root:
                    for key in ("Pos", "Dimension", "XpLevel", "XpTotal", "Health", "foodLevel", "Inventory", "EnderItems"):
                        if key in root:
                            info["details"][key] = root[key]
            except Exception as e:
                self._logger.warn(f"Error parsing NBT: {e}")
                info["details"]["error"] = str(e)

            self._append_result(file_path, "dat", os.path.getsize(file_path), info)

    def _process_json_file(self, file_path: str) -> None:
        info = {}
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                info["keys"] = list(data.keys())
        except Exception as e:
            self._logger.warn(f"Error parsing JSON: {e}")
            info["error"] = str(e)

        self._append_result(file_path, "json", os.path.getsize(file_path), info)

    def _append_result(self, file_path, type, size, details) -> None:
        self._results.append({
            "file": file_path,
            "type": type,
            "size": size,
            "details": details
        })

    def get_results(self):
        return self._results
