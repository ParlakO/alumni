import asyncio
from app.main import (
    app, users_db,
    health_check, get_users, get_user_by_id,
    create_user, update_user, patch_user, delete_user,
    get_hello, get_hello_name, get_sum, get_about
)
from app.models import UserCreate, UserUpdate, UserPatch
from fastapi import HTTPException

async def main():
    print("=== TESTING ALL ALUMNI SYSTEM ENDPOINTS ===")

    # 1. /hello
    hello = await get_hello()
    assert hello == {"message": "Hello, World!"}
    print("PASS: GET /hello ->", hello)

    # 2. /hello/:name
    hello_name = await get_hello_name("Osman")
    assert hello_name == {"message": "Hello, Osman!"}
    print("PASS: GET /hello/Osman ->", hello_name)

    # 3. /sum/:a/:b
    sum_res = await get_sum(15, 27)
    assert sum_res == {"a": 15, "b": 27, "sum": 42}
    print("PASS: GET /sum/15/27 ->", sum_res)

    # 4. /about
    about = await get_about()
    assert "project" in about and "architecture" in about
    print("PASS: GET /about ->", about["project"], "-", about["architecture"])

    # 5. /api/health
    h = await health_check()
    assert h == {"status": "ok", "message": "Alumni System API is healthy and running"}
    print("PASS: GET /api/health ->", h)

    # 6. /api/users (Ordered by ID)
    users = await get_users()
    assert len(users) == 2
    assert users[0]["id"] <= users[1]["id"]
    print(f"PASS: GET /api/users (Ordered by ID) -> {[u['id'] for u in users]}")

    # 7. /api/users/:id
    u1 = await get_user_by_id(1)
    assert u1["name"] == "Osman Parlak"
    print("PASS: GET /api/users/1 ->", u1["name"])

    # 8. POST /api/users duplicate check
    try:
        await create_user(UserCreate(id=1, name="Dup", email="dup@example.com", department="MIS"))
        assert False, "Should raise 400"
    except HTTPException as e:
        assert e.status_code == 400
        assert e.detail == "User ID already exists"
        print("PASS: POST /api/users duplicate check -> 400")

    # 9. POST /api/users create new
    new_u = await create_user(UserCreate(id=5, name="Zeynep Kaya", email="zeynep@example.com", department="Industrial Engineering"))
    assert new_u["id"] == 5
    print("PASS: POST /api/users create -> ID 5")

    # 10. PUT /api/users/:id
    put_u = await update_user(5, UserUpdate(name="Zeynep Kaya Parlak", email="zeynep.p@example.com", department="Industrial Engineering"))
    assert put_u["name"] == "Zeynep Kaya Parlak"
    print("PASS: PUT /api/users/5 -> Updated to", put_u["name"])

    # 11. PATCH /api/users/:id
    patch_u = await patch_user(5, UserPatch(department="AI Engineering"))
    assert patch_u["department"] == "AI Engineering"
    print("PASS: PATCH /api/users/5 -> Department updated to", patch_u["department"])

    # 12. DELETE /api/users/:id
    del_res = await delete_user(5)
    assert del_res.status_code == 204
    print("PASS: DELETE /api/users/5 -> 204 No Content")

    print("\nALL 12 ENDPOINTS VERIFIED & WORKING PERFECTLY!")

if __name__ == "__main__":
    asyncio.run(main())
