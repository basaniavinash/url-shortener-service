from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="URL Shortener (Flat)", version="0.1.0")
app.include_router(router)


@app.get("/healthz", tags=["health"])
def health():
    return {"status": "ok"}
