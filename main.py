from fastapi import FastAPI


app = FastAPI(title="E-Commerce API")

@app.get("/")
def read_root():
    return {"status": "API is running"}