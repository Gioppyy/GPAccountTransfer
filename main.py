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
        bedrock = input_utils.is_arg_present("bedrock")
        dry_run = input_utils.is_arg_present("dry-run")
    except Exception as e:
        logger.error(str(e))

    cfg = Config(logger)
    logger.info("Configuration initialized")
    logger.info(f"Server path: {cfg['server_path']}")
    logger.info(f"Old username: {old_username}")
    input_utils.check_ans(logger, input("Is this correct? (y/n): "))
    logger.info(f"New username: {new_username}")
    input_utils.check_ans(logger, input("Is this correct? (y/n): "))

    if old_username == new_username:
        logger.critical("Please provide different usernames")

    if bedrock:
        old_username = cfg["bedrock_format"].replace("{username}", old_username)
        new_username = cfg["bedrock_format"].replace("{username}", new_username)
        logger.info(f"Formatted old username for Bedrock user: {old_username}")
        logger.info(f"Formatted new username for Bedrock user: {new_username}")

    logger.info("Generating UUIDs")
    uuid_utils = UUIDUtils(logger)
    old_uuid = uuid_utils.generate_offline_uuid(old_username)
    new_uuid = uuid_utils.generate_offline_uuid(new_username)
    logger.info("UUIDs generated successfully")

    logs = []
    fscanner = FolderScanner(
        logger,
        cfg["server_path"],
        old_uuid,
        old_username,
        new_uuid,
        new_username,
        dry_run
    )
    logs.extend(fscanner.scan())

    if cfg["storage_type"] != "none":
        try:
            logger.info("Scanning database...")
            mysql_scanner = MySQLScanner(
                logger,
                cfg["db_host"],
                cfg["db_port"],
                cfg["db_username"],
                cfg["db_password"]
            )
            mysql_logs = mysql_scanner.scan_all_databases(old_uuid, old_username)
            mysql_scanner.update_entries(
                mysql_logs,
                old_uuid=old_uuid,
                new_uuid=new_uuid,
                old_name=old_username,
                new_name=new_username,
                dry_run=dry_run
            )
            logs.extend(mysql_logs)
        except Exception as e:
            logger.error(f"Cannot connect to MySQL server: {e}")
    else:
        logger.info("Database scanning is disabled, skipping...")

    if cfg["backup_enabled"]:
        backup = Backupper(logger, cfg["backup_path"])
        backup.log_changes(logs)
    else:
        logger.info("Backup is disabled, skipping...")

    logger.info(f"Found and updated {len(logs)} entries for old username/UUID")

if __name__ == "__main__":
    main()
