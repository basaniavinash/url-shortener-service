import logging, sys, time
from pythonjsonlogger import jsonlogger

def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"levelname": "level"}
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

class RequestTimingMiddleware:
    def __init__(self, app):
        self.app = app
        self.log = logging.getLogger("http")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            dur_ms = (time.perf_counter() - start) * 1000
            path = scope.get("path")
            method = scope.get("method")
            self.log.info("request", extra={
                "method": method, "path": path, "status": status_code,
                "latency_ms": round(dur_ms, 2)
            })
