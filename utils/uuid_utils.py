import requests, uuid, hashlib
from utils import logger

class UUIDUtils:
    def __init__(self, logger: logger):
        self._logger = logger

    def generate_offline_uuid(self, username: str) -> str:
        offline_string = f"OfflinePlayer:{username}"
        md5_hash = hashlib.md5(offline_string.encode("utf-8")).digest()
        offline_uuid = uuid.UUID(bytes=md5_hash, version=3)
        return str(offline_uuid)

    def get_premium_uuid(self, username: str) -> str | None:
        try:
            url = f"https://api.mojang.com/users/profiles/minecraft/{username}"

            response = requests.get(url)
            if response.status_code != 200:
                self._logger.warn(f"Mojang error: {response.status_code}")
                return None

            data = response.json()
            raw_id = data["id"]
            return (
                    f"{raw_id[0:8]}-{raw_id[8:12]}-"
                    f"{raw_id[12:16]}-{raw_id[16:20]}-{raw_id[20:32]}"
                )

        except Exception as exp:
            self._logger.error(str(exp))
            return None
