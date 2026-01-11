from utils import FolderScanner, UUIDUtils, Config, MySQLScanner, Backupper
from utils import logger, input_utils
from utils.backup import MySQLEntry

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
    if (old_username == new_username):
        logger.critical("Please insert different usernames")
    logger.info("Generated successfully")

    logs = []
    fscanner = FolderScanner(logger, cfg["server_path"], old_uuid, old_username, new_uuid, new_username)
    logs.extend(fscanner.scan())

    if cfg["storage_type"] != "none":
        try:
            logger.info("Scanning database")
            mysql_scanner = MySQLScanner(logger, cfg["db_host"], cfg["db_port"], cfg["db_username"], cfg["db_password"])
            mysql_logs = mysql_scanner.scan_all_databases(old_uuid, old_username)
            mysql_scanner.update_entries(
                mysql_logs,
                old_uuid=old_uuid,
                new_uuid=new_uuid,
                old_name=old_username,
                new_name=new_username,
                dry_run=True
            )
            logs.extend(mysql_logs)
        except Exception as e:
            logger.error(f"Cant connect to MySQL server: {e}")
    else: logger.info("Database scan is disabled.. skipping")

    if cfg["backup_enabled"]:
        backup = Backupper(logger, cfg["backup_path"])
        backup.log_changes(logs)
    else: logger.info("Backup is disabled.. skipping")

    logger.info(f"Found and updated {len(logs)} entry for old name / uuid")

if __name__ == "__main__":
    main()
