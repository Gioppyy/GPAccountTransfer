from utils import logger
import sys

def check_ans(logger: logger, res: str) -> None:
    if (not res.lower() == "y" and not res.lower() == "yes"):
        logger.critical("Please make sure to insert the right info")

def get_arg(arg_name: str, default: str | int | None) -> str | bool | None:
    try:
        idx = sys.argv.index(f"--{arg_name}")
        if idx+1 >= len(sys.argv):
            return default
        return sys.argv[idx + 1]
    except ValueError:
        return default

def parse_bool(value: str) -> bool:
    return value.lower() == "true"
