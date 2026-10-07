import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    print(f"Alumni System Server starting on port {port}...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
