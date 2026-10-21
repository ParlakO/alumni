import asyncio
from app.models import UserModel, UserCreate, UserUpdate, UserPatch, user_model
from app.controllers.api_user_controller import (
    get_api_users, get_api_user_by_id, create_api_user, update_api_user, patch_api_user, delete_api_user
)
from app.controllers.user_controller import (
    list_users_view, create_user_view, show_user_view, edit_user_view,
    update_user_view, patch_user_view, delete_user_view
)
from app.main import get_hello, get_hello_name, get_sum, get_about, health_check, get_db_status
from fastapi import HTTPException
from starlette.requests import Request


def make_request(method: str = "GET", path: str = "/users") -> Request:
    """Minimal ASGI request so view handlers can be called directly."""
    return Request({"type": "http", "method": method, "path": path, "headers": [], "query_string": b""})

async def main():
    print("=============================================================")
    print("  RUNNING TESTS: USERMODEL & DUAL CONTROLLER ARCHITECTURE")
    print("=============================================================")

    # -------------------------------------------------------------
    # 1. Test UserModel directly (In-Memory Model without DB)
    # -------------------------------------------------------------
    print("\n--- 1. Testing UserModel (No DB) ---")
    model = UserModel()
    initial_users = model.get_all()
    assert len(initial_users) >= 2, f"Expected at least 2 users, got {len(initial_users)}"
    print(f"PASS: UserModel.get_all() -> {len(initial_users)} users")

    u1 = model.get_by_id(1)
    assert u1 is not None and u1["name"] == "Osman Parlak"
    print("PASS: UserModel.get_by_id(1) -> Osman Parlak")

    # Duplicate check
    try:
        model.create(UserCreate(id=1, name="Duplicate", email="dup@example.com", department="MIS"))
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "already exists" in str(e)
        print("PASS: UserModel.create() duplicate check -> ValueError")

    # Create new
    created = model.create(UserCreate(id=9010, name="Ali Veli", email="ali@example.com", department="MIS"))
    assert created["id"] == 9010
    print("PASS: UserModel.create() -> Created ID 9010")

    # Update (PUT)
    updated = model.update(9010, UserUpdate(name="Ali Veli Guncel", email="ali.g@example.com", department="MIS"))
    assert updated["name"] == "Ali Veli Guncel"
    print("PASS: UserModel.update() -> Updated name")

    # Patch (PATCH)
    patched = model.patch(9010, UserPatch(department="Software Engineering"))
    assert patched["department"] == "Software Engineering"
    print("PASS: UserModel.patch() -> Patched department")

    # Delete
    deleted = model.delete(9010)
    assert deleted is True
    assert model.get_by_id(9010) is None
    print("PASS: UserModel.delete() -> Deleted ID 9010")

    # -------------------------------------------------------------
    # 2. Test ApiUserController (/api/users)
    # -------------------------------------------------------------
    print("\n--- 2. Testing ApiUserController (/api/users) ---")
    api_users = await get_api_users()
    assert len(api_users) >= 2
    print(f"PASS: [ApiUserController] GET /api/users -> {len(api_users)} users")

    api_u1 = await get_api_user_by_id(1)
    assert api_u1["id"] == 1
    print("PASS: [ApiUserController] GET /api/users/1 -> OK")

    new_api_u = await create_api_user(UserCreate(id=9020, name="Api User", email="api@example.com", department="MIS"))
    assert new_api_u["id"] == 9020
    print("PASS: [ApiUserController] POST /api/users -> OK")

    put_api_u = await update_api_user(9020, UserUpdate(name="Api User Updated", email="api@example.com", department="MIS"))
    assert put_api_u["name"] == "Api User Updated"
    print("PASS: [ApiUserController] PUT /api/users/9020 -> OK")

    patch_api_u = await patch_api_user(9020, UserPatch(department="Computer Eng"))
    assert patch_api_u["department"] == "Computer Eng"
    print("PASS: [ApiUserController] PATCH /api/users/9020 -> OK")

    del_api_res = await delete_api_user(9020)
    assert del_api_res.status_code == 204
    print("PASS: [ApiUserController] DELETE /api/users/9020 -> 204 No Content")

    # -------------------------------------------------------------
    # 3. Test UserController (/users) - Week 4 Full CRUD with Views
    # -------------------------------------------------------------
    print("\n--- 3. Testing UserController (/users) ---")
    req = make_request()

    page = await list_users_view(req)
    html = page.body.decode()
    assert page.status_code == 200 and "Osman Parlak" in html and "<table" in html
    print("PASS: [UserController] GET /users -> list view")

    created = await create_user_view(req, name="Web User", email="web@example.com", department="IE", id="9030")
    assert created.status_code == 303 and created.headers["location"] == "/users?created=9030"
    print("PASS: [UserController] POST /users -> 303 /users")

    dup = await create_user_view(req, name="Dup", email="dup@example.com", department="IE", id="9030")
    assert dup.status_code == 400 and "User ID already exists" in dup.body.decode()
    print("PASS: [UserController] POST /users duplicate ID -> 400 view")

    show = await show_user_view(req, 9030)
    assert show.status_code == 200 and "Web User" in show.body.decode()
    print("PASS: [UserController] GET /users/9030 -> show view")

    missing = await show_user_view(req, 99999)
    assert missing.status_code == 404
    print("PASS: [UserController] GET /users/99999 -> 404 view")

    edit = await edit_user_view(req, 9030)
    assert edit.status_code == 200 and 'value="Web User"' in edit.body.decode()
    print("PASS: [UserController] GET /users/9030/edit -> edit form pre-filled")

    put_ok = await update_user_view(req, 9030, name="Web User Updated", email="web@example.com", department="IE")
    assert put_ok.status_code == 303 and user_model.get_by_id(9030)["name"] == "Web User Updated"
    print("PASS: [UserController] PUT /users/9030 -> 303, replaced")

    put_bad = await update_user_view(req, 9030, name="Only Name", email="", department="")
    assert put_bad.status_code == 400
    print("PASS: [UserController] PUT /users/9030 missing fields -> 400 view")

    patch_ok = await patch_user_view(req, 9030, name="", email="", department="Industrial Eng")
    u9030 = user_model.get_by_id(9030)
    assert patch_ok.status_code == 303 and u9030["department"] == "Industrial Eng" and u9030["name"] == "Web User Updated"
    print("PASS: [UserController] PATCH /users/9030 -> 303, only department changed")

    del_ok = await delete_user_view(req, 9030)
    assert del_ok.status_code == 303 and user_model.get_by_id(9030) is None
    print("PASS: [UserController] DELETE /users/9030 -> 303 /users")

    del_missing = await delete_user_view(req, 9030)
    assert del_missing.status_code == 404
    print("PASS: [UserController] DELETE /users/9030 again -> 404 view")

    # -------------------------------------------------------------
    # 4. Test Week 1 Core Endpoints
    # -------------------------------------------------------------
    print("\n--- 4. Testing Week 1 Core Endpoints ---")
    assert (await get_hello()) == {"message": "Hello, World!"}
    assert (await get_hello_name("Osman")) == {"message": "Hello, Osman!"}
    assert (await get_sum(7, 8)) == {"a": 7, "b": 8, "sum": 15}
    assert (await health_check()) == {"status": "ok", "message": "Alumni System API is healthy and running"}
    about = await get_about()
    assert "controllers" in about
    assert "storage" in about
    db_status = await get_db_status()
    assert db_status["status"] == "connected"
    assert db_status["current_revision"] == "4b4900ce1c26"
    print("PASS: Week 1 & 5 endpoints (/hello, /sum, /api/health, /about, /api/db-status) -> OK")

    # -------------------------------------------------------------
    # 5. Test Week 6: Direct & Nested Routes, Include, Applications
    # -------------------------------------------------------------
    print("\n--- 5. Testing Week 6: Direct & Nested Routes & Applications ---")
    from app.controllers.api_user_controller import create_user_job, get_user_jobs, get_user_applications
    from app.controllers.api_job_controller import get_all_jobs, get_job_by_id, apply_to_job, get_job_applications
    from app.models import JobPostingCreate, ApplicationCreate

    # 5.1 Nested Route: POST /api/users/:id/jobs (URL says whose posting it is)
    new_job = await create_user_job(user_id=1, job_in=JobPostingCreate(title="Cloud Engineer", company="Google"))
    assert new_job["user_id"] == 1
    assert new_job["title"] == "Cloud Engineer"
    print("PASS: [Nested Route] POST /api/users/1/jobs -> 201 Created")

    # 5.2 Nested Route 404: Non-existent user
    try:
        await create_user_job(user_id=99999, job_in=JobPostingCreate(title="Ghost", company="None"))
        assert False, "Should raise 404"
    except HTTPException as e:
        assert e.status_code == 404
        print("PASS: [Nested Route] POST /api/users/99999/jobs -> 404 User Not Found")

    # 5.3 Include Query: GET /api/users/1?include=jobs
    user_with_jobs = await get_api_user_by_id(user_id=1, include="jobs")
    assert "jobs" in user_with_jobs
    assert len(user_with_jobs["jobs"]) >= 1
    print(f"PASS: [Include] GET /api/users/1?include=jobs -> returns {len(user_with_jobs['jobs'])} jobs")

    # 5.4 Direct Route: GET /api/jobs
    all_jobs = await get_all_jobs()
    assert len(all_jobs) >= 1
    print(f"PASS: [Direct Route] GET /api/jobs -> {len(all_jobs)} jobs")

    # 5.5 Applications Route: POST /api/jobs/:id/applications (201 Created)
    app_result = await apply_to_job(job_id=new_job["id"], application_in=ApplicationCreate(userId=2))
    assert app_result["status"] == "applied"
    assert app_result["user_id"] == 2
    print("PASS: [Applications Route] POST /api/jobs/:id/applications -> 201 Created")

    # 5.6 Duplicate Application Check: (409 Conflict)
    try:
        await apply_to_job(job_id=new_job["id"], application_in=ApplicationCreate(userId=2))
        assert False, "Should raise 409 Conflict"
    except HTTPException as e:
        assert e.status_code == 409
        print("PASS: [Applications Route] Duplicate application -> 409 Conflict")

    # 5.7 RESTRICT Delete Rule: Attempt to delete user 1 who has active postings
    try:
        await delete_api_user(user_id=1)
        assert False, "Should raise 409 Conflict due to RESTRICT rule"
    except HTTPException as e:
        assert e.status_code == 409
        print("PASS: [Delete Rule] DELETE /api/users/1 with active jobs -> 409 Conflict (RESTRICT rule)")

    # 5.8 Applications Two Lists: Applications vs Applicants
    from app.controllers.api_job_controller import get_job_applicants
    from app.controllers.api_application_controller import (
        get_all_applications, get_application_by_id, update_application_status, delete_application
    )
    from app.models import ApplicationStatusUpdate

    job_apps = await get_job_applications(job_id=new_job["id"])
    assert len(job_apps) >= 1
    print(f"PASS: [Two Lists - 1] GET /api/jobs/:id/applications -> {len(job_apps)} applications")

    job_applicants = await get_job_applicants(job_id=new_job["id"])
    assert len(job_applicants) >= 1
    assert job_applicants[0]["id"] == 2
    print(f"PASS: [Two Lists - 2] GET /api/jobs/:id/applicants -> {len(job_applicants)} applicants (User objects)")

    # 5.9 Direct Applications CRUD: List, Get, Patch Status, Delete
    all_apps = await get_all_applications()
    assert len(all_apps) >= 1
    print(f"PASS: [Direct App Route] GET /api/applications -> {len(all_apps)} total applications")

    patched_app = await update_application_status(
        application_id=app_result["id"],
        status_in=ApplicationStatusUpdate(status="interview")
    )
    assert patched_app["status"] == "interview"
    print("PASS: [Direct App Route] PATCH /api/applications/:id -> status updated to 'interview'")

    del_app = await delete_application(application_id=app_result["id"])
    assert del_app.status_code == 204
    print("PASS: [Direct App Route] DELETE /api/applications/:id -> 204 No Content")

    print("\n=============================================================")
    print("  ALL TESTS PASSED SUCCESSFULLY! (Direct & Nested Routes OK)")
    print("=============================================================")

if __name__ == "__main__":
    asyncio.run(main())
