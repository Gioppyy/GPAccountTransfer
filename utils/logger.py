from datetime import datetime
import sys

_COLOR_DEBUG = "\033[1;34m"
_COLOR_INFO = "\033[1;36m"
_COLOR_WARNING = "\033[1;33m"
_COLOR_ERROR = "\033[1;31m"
_COLOR_FATAL = "\033[1;41;97m"
_COLOR_RESET   = "\033[0m"

_TIME_FMT = "%Y-%m-%d %H:%M:%S"

def date() -> str:
    return datetime.now().strftime(_TIME_FMT)

def _p(*args, **kwargs) -> None:
    print(f"[{date()}]", *args, "\033[0m", **kwargs, flush=True, file=sys.stderr)

def debug(o: object, *args, **kwargs):
    _p(f"{_COLOR_DEBUG}[DEBUG]{_COLOR_RESET}", str(o).strip(), *args, **kwargs)

def info(o: object, *args, **kwargs) -> None:
    _p(f"{_COLOR_INFO}[INFO]{_COLOR_RESET}", str(o).strip(), *args, **kwargs)

def warn(o: object, *args, **kwargs) -> None:
    _p(f"{_COLOR_WARNING}[WARN]", str(o).strip(), *args, **kwargs)

def error(o: object, *args, **kwargs) -> None:
    _p(f"{_COLOR_ERROR}[ERRO]", str(o).strip(), *args, **kwargs)

def critical(o: object, *args, **kwargs) -> None:
    _p(f"{_COLOR_FATAL}[CRIT]", str(o).strip(), *args, **kwargs)
    sys.exit(0)
