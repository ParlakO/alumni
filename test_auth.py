"""
Comprehensive Authentication & Authorization Test Suite
Verifies all whiteboard & slide requirements:
1. bcrypt password hashing + salt (same password -> 2 different hashes, never exposed in API)
2. POST /api/register, POST /api/login, POST /api/logout, GET /api/me
3. AuthMiddleware: no card / bad card -> 401 {"error": "login required"}, card BEFORE validation (401 not 400)
4. Permission matrix for guest, graduate, and admin (401 vs 403)
5. Ownership rules ("Yours, Not Someone Else's"): spoofed userId ignored on apply, posting for B -> 403, delete -> admin only
6. Admin panel (/admin), user-specific pages (/me, /my-jobs, /my-applications), dynamic role navigation
"""

from starlette.testclient import TestClient
from app.auth import hash_password, verify_password
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def _login(email: str, password: str) -> str:
    res = client.post("/api/login", json={"email": email, "password": password})
    assert res.status_code == 200, f"Login failed for {email}: {res.status_code} {res.text}"
    return res.json()["token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_password_hashing_salted():
    print("\n--- 1. Testing bcrypt Password Hashing (Salt & Never ==) ---")
    h1 = hash_password("secret123")
    h2 = hash_password("secret123")
    assert h1.startswith("$2b$12$")
    assert h1 != h2, "Same password must produce two different salted hashes"
    assert verify_password("secret123", h1)
    assert verify_password("secret123", h2)
    assert not verify_password("wrongpass", h1)
    print("PASS: bcrypt generates unique salted hashes and verifies cleanly")


def test_auth_middleware_card_before_validation():
    print("\n--- 2. Testing AuthMiddleware (401 before 400 validation) ---")
    # No card, empty body -> 401, NOT 400
    res = client.post("/api/users/1/jobs", json={})
    assert res.status_code == 401, f"Expected 401, got {res.status_code}"
    assert res.json()["error"] == "login required"

    # Bad card -> 401
    res_bad = client.get("/api/users", headers={"Authorization": "Bearer invalid.jwt.token"})
    assert res_bad.status_code == 401
    assert res_bad.json()["error"] == "login required"

    # Public job postings still accessible to guest -> 200
    res_jobs = client.get("/api/jobs")
    assert res_jobs.status_code == 200
    print("PASS: AuthMiddleware returns 401 before validation & allows public /api/jobs")


def test_login_errors_and_me():
    print("\n--- 3. Testing Login Error Parity & /api/me ---")
    r1 = client.post("/api/login", json={"email": "unknown@iu.edu.tr", "password": "secret123"})
    r2 = client.post("/api/login", json={"email": "ada@iu.edu.tr", "password": "wrongpassword"})
    assert r1.status_code == 401 and r2.status_code == 401
    assert r1.json()["error"] == "invalid email or password"
    assert r2.json()["error"] == "invalid email or password"

    ada_token = _login("ada@iu.edu.tr", "secret123")
    me = client.get("/api/me", headers=_auth_header(ada_token))
    assert me.status_code == 200
    me_data = me.json()
    assert me_data["email"] == "ada@iu.edu.tr"
    assert me_data["role"] == "graduate"
    assert "password_hash" not in me_data
    print("PASS: Identical 401 on bad email/password and /api/me returns safe claims")


def test_permission_matrix_and_ownership():
    print("\n--- 4. Testing Permission Matrix & Ownership Rules ---")
    ada_token = _login("ada@iu.edu.tr", "secret123")
    can_token = _login("can@iu.edu.tr", "secret123")
    admin_token = _login("osman@iu.edu.tr", "admin123")

    # GET /api/users -> no password_hash ever
    users_res = client.get("/api/users", headers=_auth_header(ada_token))
    assert users_res.status_code == 200
    for u in users_res.json():
        assert "password_hash" not in u

    # Graduate cannot sign up again -> 403
    reg_as_grad = client.post(
        "/api/register",
        headers=_auth_header(ada_token),
        json={"name": "New", "email": "newgrad@iu.edu.tr", "department": "MIS", "password": "secret123"},
    )
    assert reg_as_grad.status_code == 403

    # Graduate A cannot post a job for B -> 403
    post_for_other = client.post(
        "/api/users/2/jobs",
        headers=_auth_header(ada_token),
        json={"title": "Spoofed Job", "company": "EvilCorp"},
    )
    assert post_for_other.status_code == 403
    assert post_for_other.json()["error"] == "not allowed"

    # Graduate A CAN post a job for self -> 201
    post_for_self = client.post(
        "/api/users/1/jobs",
        headers=_auth_header(ada_token),
        json={"title": "Auth Tested Job", "company": "Acme"},
    )
    assert post_for_self.status_code == 201
    job_id = post_for_self.json()["id"]

    # Graduate B applies with spoofed userId=1 -> ignored! applicant MUST be B (id=2)
    apply_res = client.post(
        f"/api/jobs/{job_id}/applications",
        headers=_auth_header(can_token),
        json={"userId": 1},
    )
    assert apply_res.status_code == 201
    assert apply_res.json()["user_id"] == 2, "Spoofed userId in body must be ignored"

    # Admin CANNOT apply to a job -> 403
    admin_apply = client.post(
        f"/api/jobs/{job_id}/applications",
        headers=_auth_header(admin_token),
        json={},
    )
    assert admin_apply.status_code == 403

    # Graduate A cannot edit B's profile -> 403
    edit_other = client.patch(
        "/api/users/2",
        headers=_auth_header(ada_token),
        json={"name": "Hacked"},
    )
    assert edit_other.status_code == 403

    # Guest registers a temporary user -> 201
    guest_client = TestClient(app, raise_server_exceptions=False)
    reg_res = guest_client.post(
        "/api/register",
        json={"name": "Temp Grad", "email": "temp.grad.test@iu.edu.tr", "department": "MIS", "password": "secret123"},
    )
    assert reg_res.status_code == 201
    temp_id = reg_res.json()["user"]["id"]
    assert reg_res.json()["user"]["role"] == "graduate"

    # Graduate cannot delete a user -> 403
    del_by_grad = client.delete(f"/api/users/{temp_id}", headers=_auth_header(ada_token))
    assert del_by_grad.status_code == 403

    # Admin can promote & delete user -> 200 / 204
    role_res = client.patch(
        f"/api/admin/users/{temp_id}/role",
        headers=_auth_header(admin_token),
        json={"role": "admin"},
    )
    assert role_res.status_code == 200 and role_res.json()["role"] == "admin"

    del_by_admin = client.delete(f"/api/users/{temp_id}", headers=_auth_header(admin_token))
    assert del_by_admin.status_code == 204

    # Clean up test job
    client.delete(f"/api/jobs/{job_id}", headers=_auth_header(admin_token))
    print("PASS: All permission matrix & ownership rules enforced accurately")


def test_views_dynamic_nav_and_admin_panel():
    print("\n--- 5. Testing Dynamic Navigation, User-Specific Pages & Admin Panel ---")
    # Guest visiting /me or /admin -> redirected to /login
    guest = TestClient(app, raise_server_exceptions=False)
    r_me_guest = guest.get("/me", follow_redirects=False)
    assert r_me_guest.status_code == 303 and "/login" in r_me_guest.headers["location"]

    r_admin_guest = guest.get("/admin", follow_redirects=False)
    assert r_admin_guest.status_code == 303 and "/login" in r_admin_guest.headers["location"]

    # Login page renders
    assert guest.get("/login").status_code == 200
    assert guest.get("/register").status_code == 200

    # Graduate sees /me, /my-jobs, /my-applications, and gets 403 on /admin
    grad_client = TestClient(app, raise_server_exceptions=False)
    ada_token = _login("ada@iu.edu.tr", "secret123")
    grad_client.cookies.set("access_token", ada_token)

    me_html = grad_client.get("/me").text
    assert "Profilim" in me_html and "İlanlarım" in me_html and "Admin Paneli" not in me_html
    assert grad_client.get("/my-jobs").status_code == 200
    assert grad_client.get("/my-applications").status_code == 200
    assert grad_client.get("/admin").status_code == 403

    # Admin sees /admin and dynamic Admin Paneli link
    admin_client = TestClient(app, raise_server_exceptions=False)
    admin_token = _login("osman@iu.edu.tr", "admin123")
    admin_client.cookies.set("access_token", admin_token)

    admin_res = admin_client.get("/admin")
    assert admin_res.status_code == 200
    assert "Admin Paneli" in admin_res.text and "Kullanıcı ve Rol Yönetimi" in admin_res.text
    print("PASS: Dynamic navigation, user-specific pages, and Admin Panel verified")


if __name__ == "__main__":
    print("=============================================================")
    print("  RUNNING TESTS: AUTHENTICATION, AUTHORIZATION & ADMIN PANEL")
    print("=============================================================")
    test_password_hashing_salted()
    test_auth_middleware_card_before_validation()
    test_login_errors_and_me()
    test_permission_matrix_and_ownership()
    test_views_dynamic_nav_and_admin_panel()
    print("\n=============================================================")
    print("  ALL AUTH & AUTHORIZATION TESTS PASSED!")
    print("=============================================================")
