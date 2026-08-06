"""
Vercel Serverless Function entrypoint for AeroScrape.
Wraps the FastAPI ASGI app to normalize Vercel serverless path prefixes
BEFORE Starlette's router evaluates the request.
"""
import os
import sys

# Add both current file parent directory and working directory to Python path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from aeroscrape.web.app import app as _fastapi_app


async def app(scope, receive, send):
    """
    ASGI wrapper around FastAPI that normalizes Vercel serverless paths
    (e.g., /api/index.py/api/search -> /api/search) before routing.
    """
    if scope["type"] == "http":
        path = scope.get("path", "")
        for prefix in ["/api/index.py", "/api/index", "/index.py", "/index"]:
            if path.startswith(prefix):
                path = path[len(prefix):]
                if not path.startswith("/"):
                    path = "/" + path
                scope["path"] = path
                break
        if path == "" or not path.startswith("/"):
            scope["path"] = "/" + path
    await _fastapi_app(scope, receive, send)
