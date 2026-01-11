from dotenv import load_dotenv
from utils import logger
from utils.input_utils import parse_bool
import os

class Config:
    def __init__(self, logger: logger, env_file: str = ".env"):
        load_dotenv(env_file)

        self._logger = logger
        self._settings = {}

        self._settings["storage_type"] = os.getenv("STORAGE_TYPE") or "none"

        self._settings["db_host"] = os.getenv("DATABASE_HOST", "127.0.0.1")
        self._settings["db_port"] = int(os.getenv("DATABASE_PORT", "3306"))
        self._settings["db_username"] = os.getenv("DATABASE_USERNAME", "root")
        self._settings["db_password"] = os.getenv("DATABASE_PASSWORD", "")

        self._settings["server_path"] = os.getenv("SERVER_PATH")
        self._settings["bedrock_format"] = os.getenv("BEDROCK_FORMAT") or ".{username}"
        self._settings["backup_enabled"] = parse_bool(os.getenv("BACKUP_ENABLED", "true"))
        self._settings["backup_path"] = os.getenv("BACKUP_PATH") or "./backup"

        self._validate()

    def _validate(self):
        if not os.path.isabs(self._settings["server_path"]):
            self._logger.error("SERVER_PATH deve essere un path assoluto")

    def __getitem__(self, key: str):
        return self._settings[key]
