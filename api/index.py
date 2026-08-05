"""
Vercel Serverless Function entrypoint for AeroScrape.
Routes all Vercel requests to the FastAPI ASGI application.
"""
import os
import sys

# Ensure project root is in python path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from aeroscrape.web.app import app
