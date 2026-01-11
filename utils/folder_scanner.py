from .sqlite_scanner import SQLITEScanner
from .backup import Backupper
from utils import logger
from tqdm import tqdm
import json
import os

try:
    import nbtlib
    NBT_AVAILABLE = True
except ImportError:
    NBT_AVAILABLE = False
    logger.warn("nbtlib not installed: NBT files will not be parsed")

TEXT_EXTENSIONS = [".json", ".yml", ".yaml", ".txt"]

class FolderScanner:
    def __init__(self, logger: logger, server_path: str, old_uuid: str, old_name: str, new_uuid: str, new_name: str, dry_run: bool):
        self._db_scanner = SQLITEScanner(logger)
        self._server_path = server_path
        self._old_uuid = old_uuid
        self._old_name = old_name
        self._new_uuid = new_uuid
        self._new_name = new_name
        self._dry_run = dry_run
        self._logger = logger
        self._results = []

    def scan(self):
        self._logger.info("Searching for any entry")

        for dirpath, _, filenames in tqdm(os.walk(self._server_path), desc="Scanning folders"):

            renamed_files = {}
            for fname in filenames:
                for suffix in [self._old_uuid, self._old_name]:
                    if suffix in fname:
                        old_path = os.path.join(dirpath, fname)
                        new_fname = fname.replace(self._old_uuid, self._new_uuid).replace(self._old_name, self._new_name)
                        new_path = os.path.join(dirpath, new_fname)
                        try:
                            self._results.append(Backupper.make_rename(old_path))
                            if not self._dry_run:
                                os.rename(old_path, new_path)
                                renamed_files[fname] = new_fname
                        except Exception as e:
                            self._logger.warn(f"Cannot rename file {old_path}: {e}")
                        break

            current_filenames = [renamed_files.get(f, f) for f in filenames]
            db_files = [f for f in current_filenames if f.endswith(".db") or f.endswith(".sqlite")]
            for db_file in tqdm(db_files, desc=f"Scanning DBs in {dirpath}", leave=False):
                db_path = os.path.join(dirpath, db_file)
                db_res = self._db_scanner.scan_and_update(
                    file_path=db_path,
                    old_uuid=self._old_uuid,
                    new_uuid=self._new_uuid,
                    old_name=self._old_name,
                    new_name=self._new_name,
                    dry_run=self._dry_run
                )
                self._results.extend(db_res)

            text_files = [f for f in current_filenames if any(f.lower().endswith(ext) for ext in TEXT_EXTENSIONS)]
            for text_file in tqdm(text_files, desc=f"Scanning text files in {dirpath}", leave=False):
                file_path = os.path.join(dirpath, text_file)
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    new_content = content.replace(self._old_uuid, self._new_uuid).replace(self._old_name, self._new_name)
                    if new_content != content:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(new_content)
                        self._results.append(Backupper.make_edited(file_path))
                except Exception as e:
                    self._logger.warn(f"Cannot process text file {file_path}: {e}")

        return self._results
