from fastapi import FastAPI

app = FastAPI()

# 1. Ana sayfa
@app.get("/")
def read_root():
    return {"message": "Welcome to Alumni Tracking System"}

# 2. Genel hello
@app.get("/hello")
def say_hello():
    return {"message": "Hello, World!"}

# 3. Dinamik isimle hello
@app.get("/hello/{name}")
def say_hello_name(name: str):
    return {"message": f"Hello, {name}"}

# 4. İki sayıyı toplama
@app.get("/sum/{a}/{b}")
def calculate_sum(a: int, b: int):
    return {"a": a, "b": b, "result": a + b}

# 5. Hakkında sayfası
@app.get("/about")
def get_about():
    return {
        "project": "Alumni Tracking System",
        "course": "Web Programming - YBSB3001",
        "author": "Osman Parlak"
    }