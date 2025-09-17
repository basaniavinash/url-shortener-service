from fastapi import FastAPI
from app.logging_setup import setup_logging, RequestTimingMiddleware

setup_logging()
app = FastAPI(title="URL Shortener", version="0.1.0")

# cheap health (no DB call)
@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# add middleware early
app.add_middleware(RequestTimingMiddleware)

# If you have DB engine/session, cleanly dispose at shutdown:
from app.repo import engine  # adjust import if different
@app.on_event("shutdown")
def shutdown_event():
    try:
        engine.dispose(close=True)
    except Exception:
        pass

# include your routers after app is created
from app.routes import router  # your existing API routes
app.include_router(router)
