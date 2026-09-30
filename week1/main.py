from fastapi import FastAPI

app = FastAPI(title="Alumni System - Week 1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Alumni Tracking System API!"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Week 1 API is running smoothly"}