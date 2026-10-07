import asyncio
from app.models import UserModel, UserCreate, UserUpdate, UserPatch
from app.controllers.api_user_controller import (
    get_api_users, get_api_user_by_id, create_api_user, update_api_user, patch_api_user, delete_api_user
)
from app.controllers.user_controller import (
    get_users, get_user_by_id, create_user, update_user, patch_user, delete_user
)
from app.main import get_hello, get_hello_name, get_sum, get_about, health_check
from fastapi import HTTPException

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
    assert len(initial_users) == 2, f"Expected 2 users, got {len(initial_users)}"
    print(f"PASS: UserModel.get_all() -> {len(initial_users)} initial users")

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
    created = model.create(UserCreate(id=10, name="Ali Veli", email="ali@example.com", department="MIS"))
    assert created["id"] == 10
    print("PASS: UserModel.create() -> Created ID 10")

    # Update (PUT)
    updated = model.update(10, UserUpdate(name="Ali Veli Guncel", email="ali.g@example.com", department="MIS"))
    assert updated["name"] == "Ali Veli Guncel"
    print("PASS: UserModel.update() -> Updated name")

    # Patch (PATCH)
    patched = model.patch(10, UserPatch(department="Software Engineering"))
    assert patched["department"] == "Software Engineering"
    print("PASS: UserModel.patch() -> Patched department")

    # Delete
    deleted = model.delete(10)
    assert deleted is True
    assert model.get_by_id(10) is None
    print("PASS: UserModel.delete() -> Deleted ID 10")

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

    new_api_u = await create_api_user(UserCreate(id=20, name="Api User", email="api@example.com", department="MIS"))
    assert new_api_u["id"] == 20
    print("PASS: [ApiUserController] POST /api/users -> OK")

    put_api_u = await update_api_user(20, UserUpdate(name="Api User Updated", email="api@example.com", department="MIS"))
    assert put_api_u["name"] == "Api User Updated"
    print("PASS: [ApiUserController] PUT /api/users/20 -> OK")

    patch_api_u = await patch_api_user(20, UserPatch(department="Computer Eng"))
    assert patch_api_u["department"] == "Computer Eng"
    print("PASS: [ApiUserController] PATCH /api/users/20 -> OK")

    del_api_res = await delete_api_user(20)
    assert del_api_res.status_code == 204
    print("PASS: [ApiUserController] DELETE /api/users/20 -> 204 No Content")

    # -------------------------------------------------------------
    # 3. Test UserController (/users)
    # -------------------------------------------------------------
    print("\n--- 3. Testing UserController (/users) ---")
    users = await get_users()
    assert len(users) >= 2
    print(f"PASS: [UserController] GET /users -> {len(users)} users")

    u2 = await get_user_by_id(2)
    assert u2["id"] == 2
    print("PASS: [UserController] GET /users/2 -> Ahmet Yilmaz")

    new_u = await create_user(UserCreate(id=30, name="Web User", email="web@example.com", department="IE"))
    assert new_u["id"] == 30
    print("PASS: [UserController] POST /users -> OK")

    put_u = await update_user(30, UserUpdate(name="Web User Updated", email="web@example.com", department="IE"))
    assert put_u["name"] == "Web User Updated"
    print("PASS: [UserController] PUT /users/30 -> OK")

    patch_u = await patch_user(30, UserPatch(department="Industrial Eng"))
    assert patch_u["department"] == "Industrial Eng"
    print("PASS: [UserController] PATCH /users/30 -> OK")

    del_res = await delete_user(30)
    assert del_res.status_code == 204
    print("PASS: [UserController] DELETE /users/30 -> 204 No Content")

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
    print("PASS: Week 1 endpoints (/hello, /hello/:name, /sum/:a/:b, /api/health, /about) -> OK")

    print("\n=============================================================")
    print("  ALL TESTS PASSED SUCCESSFULLY! (UserModel & 2 Controllers)")
    print("=============================================================")

if __name__ == "__main__":
    asyncio.run(main())
