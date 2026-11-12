import os
import time
from datetime import datetime
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from app.logger import format_terminal_log, log_error_to_file


class LoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware #3: Logger Middleware
    Logs every request to the terminal in the format:
      time method route res type duration
    Example:
      10:20:30 POST /users 201 18ms
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        time_str = datetime.now().strftime("%H:%M:%S")
        method = request.method
        route = request.url.path

        try:
            response = await call_next(request)
            duration_ms = int(round((time.perf_counter() - start_time) * 1000))
            status_code = response.status_code
            print(format_terminal_log(time_str, method, route, status_code, duration_ms))
            return response
        except Exception as exc:
            duration_ms = int(round((time.perf_counter() - start_time) * 1000))
            print(format_terminal_log(time_str, method, route, 500, duration_ms))
            # 5xx Guardian & Logger will record details to error.logs
            log_error_to_file(method, route, 500, str(exc), exc)
            raise exc


class Guardian404Middleware(BaseHTTPMiddleware):
    """
    Middleware #4 & #7: 404 Guardian Middleware
    - Intercepts 404 Not Found responses.
    - Returns structured 404 errors with a clear reason.
    - If request is a web browser request (HTML), redirects to generic /404 page.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if response.status_code == 404:
            accept_header = request.headers.get("accept", "")
            is_browser_request = "text/html" in accept_header and not request.url.path.startswith("/api")

            # Browser redirect to generic 404 page (Task #7)
            if is_browser_request and request.url.path != "/404":
                return RedirectResponse(
                    url=f"/404?path={request.url.path}",
                    status_code=303
                )

        return response

