import os
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_logger_middleware_and_normal_request():
    print("\n--- Testing 1: Normal Request & Logger Middleware ---")
    res = client.get("/hello")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello, World!"}
    print("PASS: Normal Request /hello -> 200 OK")


def test_404_guardian_api_with_reason():
    print("\n--- Testing 2: 404 Guardian for API Requests ---")
    res = client.get("/api/non-existent-endpoint")
    assert res.status_code == 404
    data = res.json()
    assert data["status_code"] == 404
    assert data["error"] == "Not Found"
    assert "reason" in data
    assert len(data["reason"]) > 0
    print(f"PASS: 404 Guardian returned reason: {data['reason']}")

    # 404 on non-existent resource in existing controller
    res2 = client.get("/api/users/999999")
    assert res2.status_code == 404
    data2 = res2.json()
    assert "reason" in data2
    print(f"PASS: 404 Guardian on resource returned reason: {data2['reason']}")


def test_generic_404_page_and_browser_redirect():
    print("\n--- Testing 3: Generic 404 Page & Browser Redirect ---")
    # Browser request to invalid route -> 303 Redirect to /404
    res = client.get("/some/invalid/browser/page", headers={"accept": "text/html,application/xhtml+xml"}, follow_redirects=False)
    assert res.status_code == 303
    assert "/404?path=/some/invalid/browser/page" in res.headers["location"]
    print("PASS: Browser request redirected to /404 page")

    # Visiting /404 generic page directly
    res_page = client.get("/404?path=/unknown")
    assert res_page.status_code == 404
    html = res_page.text
    assert "404" in html
    assert "Sayfa veya Kaynak Bulunamadı" in html
    print("PASS: Generic 404 page rendered correctly with message and return buttons")


def test_job_posting_rules_and_invalid_requests():
    print("\n--- Testing 4: JobPosting Validation Rules (Whiteboard #2 & #1) ---")
    # Title missing -> 400 Bad Request
    res1 = client.post("/api/users/1/jobs", json={"company": "Acme"})
    assert res1.status_code == 400
    assert "title" in res1.json()["reason"]
    print(f"PASS: Title required check -> 400 Bad Request ({res1.json()['reason']})")

    # Company missing -> 400 Bad Request
    res2 = client.post("/api/users/1/jobs", json={"title": "Junior Developer"})
    assert res2.status_code == 400
    assert "company" in res2.json()["reason"]
    print(f"PASS: Company required check -> 400 Bad Request ({res2.json()['reason']})")

    # Max 120 characters rule: 125 characters -> 400 Bad Request
    long_title = "A" * 125
    res3 = client.post("/api/users/1/jobs", json={"title": long_title, "company": "Acme"})
    assert res3.status_code == 400
    assert "at most 120" in res3.json()["reason"]
    print(f"PASS: Max 120 characters check -> 400 Bad Request ({res3.json()['reason']})")

    # Valid JobPosting with optional city and description
    res4 = client.post(
        "/api/users/1/jobs",
        json={
            "title": "Senior Cloud Engineer",
            "company": "Trendyol",
            "city": "Istanbul",
            "description": "Kubernetes and FastAPI architecture"
        }
    )
    assert res4.status_code == 201
    job_data = res4.json()
    assert job_data["title"] == "Senior Cloud Engineer"
    assert job_data["company"] == "Trendyol"
    assert job_data["city"] == "Istanbul"
    assert job_data["description"] == "Kubernetes and FastAPI architecture"
    print("PASS: Valid JobPosting with city & description created -> 201 Created")


def test_5xx_guardian_and_error_logging():
    print("\n--- Testing 5: 5xx Guardian & logs/error.logs (Whiteboard #5 & #6) ---")
    log_file_path = os.path.join("logs", "error.logs")
    initial_size = os.path.getsize(log_file_path) if os.path.exists(log_file_path) else 0

    res = client.get("/api/test-500")
    assert res.status_code == 500
    data = res.json()
    assert data["status_code"] == 500
    assert data["error"] == "Internal Server Error"
    assert "reason" in data
    print(f"PASS: 5xx Guardian caught error and returned 500: {data['reason']}")

    # Verify logs/error.logs was written
    assert os.path.exists(log_file_path)
    new_size = os.path.getsize(log_file_path)
    assert new_size > initial_size
    with open(log_file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "ERROR 500" in content
    assert "/api/test-500" in content
    print("PASS: Error details successfully written to logs/error.logs")


if __name__ == "__main__":
    print("=============================================================")
    print("  RUNNING TESTS: MIDDLEWARES, GUARDIANS & ERROR LOGGING")
    print("=============================================================")
    test_logger_middleware_and_normal_request()
    test_404_guardian_api_with_reason()
    test_generic_404_page_and_browser_redirect()
    test_job_posting_rules_and_invalid_requests()
    test_5xx_guardian_and_error_logging()
    print("\n=============================================================")
    print("  ALL MIDDLEWARE & GUARDIAN TESTS PASSED!")
    print("=============================================================")

