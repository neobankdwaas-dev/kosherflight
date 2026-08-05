"""
Vercel Serverless Function entrypoint for AeroScrape.
Routes all Vercel requests to the FastAPI ASGI application.
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

from aeroscrape.web.app import app
