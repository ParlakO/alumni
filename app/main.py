import os
from urllib.parse import parse_qs
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.controllers import api_user_controller, user_controller

# ===================================================================
# SWAGGER & APPLICATION CONFIGURATION (WEEK 1 - WEEK 4 PROGRESSION)
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
    """[Week 1 & 4] Returns project metadata and architectural overview."""
    return {
        "project": "Alumni Tracking System",
        "course": "YBSB3001 - Web Programming",
        "institution": "Istanbul University",
        "architecture": "MVC (Model-View-Controller)",
        "models": "UserModel (In-Memory, No DB connection)",
        "controllers": ["UserController (/users)", "ApiUserController (/api/users)"],
        "version": "1.0.0",
        "author": "Osman Parlak"
    }


@app.get("/api/health", summary="Health Check", tags=["Week 1 - Core & Utilities"])
async def health_check():
    """[Week 1] Health check endpoint returning API status."""
    return {"status": "ok", "message": "Alumni System API is healthy and running"}


# ===================================================================
# WEEK 4: Register Controllers (UserController & ApiUserController)
# ===================================================================

# Controller 1: /api/users
app.include_router(api_user_controller.router)

# Controller 2: /users
app.include_router(user_controller.router)


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    print(f"Alumni System Server running on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
