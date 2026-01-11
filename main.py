from utils import FolderScanner, UUIDUtils, Config, MySQLScanner
from utils import logger, input_utils

def main():
    print(r"""
 _____ ______  ___                            _ _____                    __
|  __ \| ___ \/ _ \                          | |_   _|                  / _|
| |  \/| |_/ / /_\ \ ___ ___ ___  _   _ _ __ | |_| |_ __ __ _ _ __  ___| |_ ___ _ __
| | __ |  __/|  _  |/ __/ __/ _ \| | | | '_ \| __| | '__/ _` | '_ \/ __|  _/ _ \ '__|
| |_\ \| |   | | | | (_| (_| (_) | |_| | | | | |_| | | | (_| | | | \__ \ ||  __/ |
 \____/\_|   \_| |_/\___\___\___/ \__,_|_| |_|\__\_/_|  \__,_|_| |_|___/_| \___|_|
""")

    try:
        old_username = input_utils.get_arg("old-name", "user1")
        new_username = input_utils.get_arg("new-name", "user2")
        bedrock = input_utils.parse_bool(input_utils.get_arg("bedrock", "false"))
    except Exception as e:
        logger.error(str(e))

    cfg = Config(logger)
    logger.info("Config initialized")
    logger.info(f"Server PATH: {cfg["server_path"]}")
    logger.info(f"old username: {old_username}")
    input_utils.check_ans(logger, input("Correct (y/n)? "))
    logger.info(f"new username: {new_username}")
    input_utils.check_ans(logger, input("Correct (y/n)? "))

    if bedrock:
        new_username = cfg["bedrock_format"].replace("{username}", new_username)
        logger.info(f"formatted username for bedrock user: {new_username}")
    logger.info("Getting and generating uuid")
    uuid_utils = UUIDUtils(logger)
    old_uuid = uuid_utils.generate_offline_uuid(old_username)
    new_uuid = uuid_utils.generate_offline_uuid(new_username)

    logger.debug(f"{old_uuid = } | {new_uuid = }")

    if (old_username == new_username):
        logger.critical("Please insert different usernames")
    logger.info("Generated successfully")

    fscanner = FolderScanner(logger, cfg["server_path"], old_uuid, old_username)
    fscanner.scan()

    try:
        logger.info("Scanning database")
        mysql_scanner = MySQLScanner(logger, cfg["db_host"], cfg["db_port"], cfg["db_username"], cfg["db_password"])
        res = mysql_scanner.scan_all_databases(old_uuid, old_username)
        logger.info(f"Found {len(res)} entry in the database for old name / uuid")
    except Exception as e:
        logger.error(f"Cant connect to MySQL server: {e}")

if __name__ == "__main__":
    main()
