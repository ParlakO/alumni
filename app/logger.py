import os
import time
import traceback
from datetime import datetime
from typing import Optional
from starlette.requests import Request
from starlette.responses import Response

LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
ERROR_LOG_PATH = os.path.join(LOGS_DIR, "error.logs")


def format_terminal_log(time_str: str, method: str, route: str, status_code: int, duration_ms: int) -> str:
    """
    Formats the terminal log according to the rule:
    time method route res type duration
    Example: 10:20:30 POST /users 201 18ms
    """
    return f"{time_str} {method} {route} {status_code} {duration_ms}ms"


def log_error_to_file(
    method: str,
    path: str,
    status_code: int,
    reason: str,
    exc: Optional[Exception] = None
) -> None:
    """
    Appends error entries to logs/error.logs.
    """
    os.makedirs(LOGS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_str = ""
    if exc is not None:
        tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))

    entry = (
        f"[{timestamp}] ERROR {status_code}\n"
        f"Route: {method} {path}\n"
        f"Reason: {reason}\n"
    )
    if tb_str:
        entry += f"Traceback:\n{tb_str}"
    entry += "-" * 70 + "\n"

    try:
        with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        print(f"Error writing to error.logs: {e}")

