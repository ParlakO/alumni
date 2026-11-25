import re
import time
from datetime import datetime
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, RedirectResponse
from app.logger import format_terminal_log, log_error_to_file
from app.auth import extract_token_from_request, decode_access_token
from app.models import user_model


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Auth Middleware ("The Bouncer Checks the Card"):
    - Reads JWT from `Authorization: Bearer <token>` header or `access_token` cookie.
    - Attaches `request.state.user` (dict with id, name, email, department, role) or None (guest).
    - Enforces authentication BEFORE route body validation on protected `/api/*` routes:
      no card / bad card / expired -> 401 {"error": "login required"} (401, not 400).
    """

    # Public API routes that guests may call without a token
    PUBLIC_API_EXACT = {
        ("GET", "/api/health"),
        ("GET", "/api/db-status"),
        ("GET", "/api/test-500"),
        ("POST", "/api/login"),
        ("POST", "/api/logout"),
        ("POST", "/api/register"),
        ("GET", "/api/jobs"),
        ("POST", "/api/users"),
    }
    PUBLIC_JOB_DETAIL_RE = re.compile(r"^/api/jobs/\d+$")

    @classmethod
    def _is_public_api_route(cls, method: str, path: str) -> bool:
        m = method.upper()
        normalized = path.rstrip("/") or "/"
        if m == "OPTIONS":
            return True
        if (m, normalized) in cls.PUBLIC_API_EXACT:
            return True
        if m == "GET" and cls.PUBLIC_JOB_DETAIL_RE.match(normalized):
            return True
        return False

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        token = extract_token_from_request(request)
        current_user = None

        if token and token != "__INVALID_AUTH_HEADER__":
            claims = decode_access_token(token)
            if claims:
                # Refresh from DB so role updates or deleted accounts take effect immediately
                db_user = user_model.get_by_id(claims["id"])
                if db_user:
                    current_user = db_user

        request.state.user = current_user

        path = request.url.path
        if path.startswith("/api") and not self._is_public_api_route(request.method, path):
            if current_user is None:
                return JSONResponse(
                    status_code=401,
                    content={
                        "status_code": 401,
                        "error": "login required",
                        "reason": "login required",
                        "detail": "login required",
                        "path": path,
                    },
                )

        return await call_next(request)


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
