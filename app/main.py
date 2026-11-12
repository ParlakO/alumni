import os
from urllib.parse import parse_qs
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.controllers import api_user_controller, user_controller, api_job_controller, api_application_controller
from app.logger import log_error_to_file
from app.middleware import LoggerMiddleware, Guardian404Middleware

# ===================================================================
# SWAGGER & APPLICATION CONFIGURATION (WEEK 1 - WEEK 6 PROGRESSION)
# ===================================================================

app = FastAPI(
    title="🎓 Alumni Tracking System API (Mezun Bilgi Sistemi)",
    description="""
    ## İstanbul Üniversitesi - Web Programlama (YBSB3001)
    ### Mezun Takip Sistemi RESTful API & MVC Mimarisi

    Bu API, 4 haftalık ders kazanımlarına uygun olarak yapılandırılmıştır:

    * 🔹 **Week 1:** Temel Yönlendirmeler (Routing), Karşılama, Parametreli Mesajlar, Toplama İşlemi & Sağlık Kontrolü
    * 🔹 **Week 2:** Bellek İçi (In-Memory) Veri Yapısı, Kullanıcı Listeleme & ID ile Kullanıcı Getirme
    * 🔹 **Week 3:** Tam CRUD Operasyonları (POST, PUT, PATCH, DELETE), HTTP Durum Kodları & Pydantic Validasyonu
    * 🔹 **Week 4:** MVC Mimarisi (Veritabanı bağımsız UserModel CRUD yapısı, `UserController` ve `ApiUserController` Controller ayrımı)
    """,
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Week 1 - Core & Utilities",
            "description": "Week 1: Temel karşılama, matematiksel işlem ve sistem sağlık kontrolü uç noktaları."
        },
        {
            "name": "API Users (ApiUserController)",
            "description": "Week 4: `/api/users` rotasına bağlı, UserModel üzerinden CRUD işlemlerini yürüten API kontrolcüsü."
        },
        {
            "name": "Users (UserController)",
            "description": "Week 4 (View Layer): `/users` üzerinde tüm CRUD işlemleri HTML sayfaları ile yapılır (list, show, create, edit, PUT, PATCH, DELETE). HTML formları PUT/PATCH/DELETE için `POST ...?_method=PUT|PATCH|DELETE` kullanır."
        }
    ]
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================================================================
# WEEK 4: Method Override Middleware (for the View layer)
# HTML forms only support GET/POST. A form can send
#   POST /users/5?_method=PUT | PATCH | DELETE
# and this middleware rewrites the request method before routing,
# so UserController can use real PUT/PATCH/DELETE routes.
# ===================================================================
class MethodOverrideMiddleware:
    ALLOWED = {"PUT", "PATCH", "DELETE"}

    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["method"] == "POST":
            query = parse_qs(scope.get("query_string", b"").decode())
            override = (query.get("_method") or [""])[0].upper()
            if override in self.ALLOWED:
                scope = dict(scope, method=override)
        await self.app(scope, receive, send)


app.add_middleware(MethodOverrideMiddleware)
app.add_middleware(Guardian404Middleware)
app.add_middleware(LoggerMiddleware)

# Views directory for HTML templates
VIEWS_DIR = os.path.join(os.path.dirname(__file__), "views")
templates = Jinja2Templates(directory=VIEWS_DIR)


# ===================================================================
# GUARDIANS & EXCEPTION HANDLERS (404 Guardian & 5xx Guardian)
# ===================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_guardian(request: Request, exc: StarletteHTTPException):
    """
    Guardian Middleware / Exception Handler for HTTP Errors.
    - 404 Guardian: Returns structured 404 error with a clear reason.
    - Generic 404 redirect for web browser requests.
    - 5xx Guardian: Logs 5xx errors to logs/error.logs and returns clean error.
    """
    accept_header = request.headers.get("accept", "")
    is_browser_request = "text/html" in accept_header and not request.url.path.startswith("/api")

    if exc.status_code == 404:
        # Browser request redirect to generic 404 page
        if is_browser_request and request.url.path != "/404":
            return RedirectResponse(url=f"/404?path={request.url.path}", status_code=303)

        # API / JSON response with clear reason
        detail = exc.detail
        if detail == "Not Found":
            detail = f"The requested resource or endpoint '{request.url.path}' was not found."

        return JSONResponse(
            status_code=404,
            content={
                "status_code": 404,
                "error": "Not Found",
                "reason": detail,
                "path": request.url.path
            }
        )

    if exc.status_code >= 500:
        log_error_to_file(request.method, request.url.path, exc.status_code, str(exc.detail))
        if is_browser_request:
            return templates.TemplateResponse(
                request,
                "500.html",
                {"title": "Sunucu Hatası", "path": request.url.path, "reason": str(exc.detail)},
                status_code=exc.status_code
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error": "Internal Server Error",
                "reason": str(exc.detail),
                "path": request.url.path
            }
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "error": "HTTP Error",
            "reason": str(exc.detail),
            "detail": exc.detail,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_guardian(request: Request, exc: RequestValidationError):
    """
    Catches invalid request payloads (e.g. invalid JSON, missing required fields)
    and returns a clean 400 Bad Request response with a descriptive reason.
    """
    reasons = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        msg = err.get("msg", "invalid")
        reasons.append(f"{loc}: {msg}" if loc else msg)
    reason_str = "; ".join(reasons) or "Validation failed"

    return JSONResponse(
        status_code=400,
        content={
            "status_code": 400,
            "error": "Bad Request",
            "reason": reason_str,
            "detail": exc.errors(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def unhandled_5xx_guardian(request: Request, exc: Exception):
    """
    Middleware #5 & #6: 5xx Guardian
    Catches all unhandled exceptions, writes stack traces to logs/error.logs,
    and returns a clean, safe 500 response with reason.
    """
    log_error_to_file(request.method, request.url.path, 500, str(exc), exc)
    accept_header = request.headers.get("accept", "")
    is_browser_request = "text/html" in accept_header and not request.url.path.startswith("/api")

    if is_browser_request:
        return templates.TemplateResponse(
            request,
            "500.html",
            {
                "title": "500 - Sunucu Hatası",
                "path": request.url.path,
                "reason": "Sunucu tarafında beklenmeyen bir hata meydana geldi."
            },
            status_code=500
        )

    return JSONResponse(
        status_code=500,
        content={
            "status_code": 500,
            "error": "Internal Server Error",
            "reason": f"An unexpected server error occurred: {str(exc)}",
            "path": request.url.path
        }
    )


# ===================================================================
# GENERIC 404 PAGE (Task #7)
# ===================================================================

@app.get("/404", response_class=HTMLResponse, include_in_schema=False)
async def generic_404_view(request: Request):
    """Generic 404 page rendering for browser users."""
    path_param = request.query_params.get("path", "")
    return templates.TemplateResponse(
        request,
        "404.html",
        {
            "title": "404 - Sayfa Bulunamadı",
            "path": path_param,
            "reason": "Aradığınız sayfa, URL veya kaynak sistemde mevcut değil."
        },
        status_code=404
    )


@app.get("/api/test-500", summary="Test 500 Internal Error (5xx Guardian)", include_in_schema=False)
async def test_trigger_500():
    """Trigger intentional 500 error for testing 5xx Guardian and logs/error.logs."""
    raise RuntimeError("Intentional test server error for 5xx Guardian validation")

# Path to static frontend files
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ===================================================================
# WEEK 1: Core & Utility Endpoints
# ===================================================================

@app.get("/", summary="API Welcome Message / Web Interface", tags=["Week 1 - Core & Utilities"])
async def read_root(request: Request):
    """
    [Week 1] Returns the web portal in browser or the welcome JSON message for API clients.
    """
    accept_header = request.headers.get("accept", "")
    format_param = request.query_params.get("format", "")

    if format_param == "json" or ("application/json" in accept_header and "text/html" not in accept_header):
        return {"message": "Welcome to the Alumni Tracking System API!"}

    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {"message": "Welcome to the Alumni Tracking System API!"}


@app.get("/hello", summary="Generic Greeting", tags=["Week 1 - Core & Utilities"])
async def get_hello():
    """[Week 1] Returns a generic greeting message."""
    return {"message": "Hello, World!"}


@app.get("/hello/{name}", summary="Named Greeting", tags=["Week 1 - Core & Utilities"])
async def get_hello_name(name: str):
    """[Week 1] Returns a personalized greeting message."""
    return {"message": f"Hello, {name}!"}


@app.get("/sum/{a}/{b}", summary="Sum of Two Integers", tags=["Week 1 - Core & Utilities"])
async def get_sum(a: int, b: int):
    """[Week 1] Calculates and returns the sum of two integers."""
    return {"a": a, "b": b, "sum": a + b}


@app.get("/about", summary="Project Information", tags=["Week 1 - Core & Utilities"])
async def get_about():
    """[Week 1 & 4 & 5] Returns project metadata and architectural overview."""
    return {
        "project": "Alumni Tracking System",
        "course": "YBSB3001 - Web Programming",
        "institution": "Istanbul University",
        "architecture": "MVC (Model-View-Controller)",
        "models": "UserModel (SQLAlchemy & SQLite persistent DB)",
        "storage": "SQLite (alumni.db)",
        "migrations": "Alembic (revision: 4b4900ce1c26)",
        "controllers": ["UserController (/users)", "ApiUserController (/api/users)"],
        "version": "1.0.0",
        "author": "Osman Parlak"
    }


@app.get("/api/db-status", summary="Database & Migration Status", tags=["Week 1 - Core & Utilities"])
async def get_db_status():
    """[Week 5] Returns real-time database and migration revision status."""
    import sqlite3
    revision = "4b4900ce1c26"
    db_ok = False
    total_users = 0
    try:
        con = sqlite3.connect("alumni.db")
        row = con.execute("SELECT version_num FROM alembic_version LIMIT 1;").fetchone()
        if row:
            revision = row[0]
        cnt = con.execute("SELECT count(*) FROM users;").fetchone()
        if cnt:
            total_users = cnt[0]
        con.close()
        db_ok = True
    except Exception:
        pass

    return {
        "status": "connected" if db_ok else "error",
        "database": "SQLite (alumni.db)",
        "orm": "SQLAlchemy 2.1+",
        "migration_tool": "Alembic",
        "current_revision": revision,
        "persistent_storage": True,
        "record_count": total_users
    }


@app.get("/api/health", summary="Health Check", tags=["Week 1 - Core & Utilities"])
async def health_check():
    """[Week 1] Health check endpoint returning API status."""
    return {"status": "ok", "message": "Alumni System API is healthy and running"}


@app.post("/api/seed", summary="Seed Database with Fake Alumni Records, Jobs & Applications", tags=["Week 1 - Core & Utilities"])
async def trigger_seed(count: int = 50, reset: bool = False):
    """[Week 5 & 6: Factory & Seeder] Seeds the database with realistic alumni, jobs, and applications."""
    from seed import seed_database_all
    totals = seed_database_all(
        users_count=count,
        jobs_count=max(5, count // 3),
        apps_count=max(8, count // 2),
        reset=reset
    )
    return {
        "status": "success",
        "message": f"Successfully seeded {count} alumni, jobs, and applications",
        "totals": totals
    }


# ===================================================================
# WEEK 4: Register Controllers (UserController & ApiUserController)
# ===================================================================

# Controller 1: /api/users (Users & Nested Job/Application Routes)
app.include_router(api_user_controller.router)

# Controller 2: /api/jobs (Direct Job Postings & Applications Routes)
app.include_router(api_job_controller.router)

# Controller 3: /api/applications (Direct Applications Management Routes)
app.include_router(api_application_controller.router)

# Controller 4: /users (View Layer)
app.include_router(user_controller.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    print(f"Alumni System Server running on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
