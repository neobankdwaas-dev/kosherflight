"""
Configuration loader for AeroScrape.
Automatically loads environment variables and affiliate CPA tracking settings.
"""
import os
from pathlib import Path


def load_env_file(env_path: str = None):
    """Simple .env file loader for zero-dependency environments."""
    if env_path is None:
        # Check both project directory and workspace root
        base_dir = Path(__file__).resolve().parent
        candidates = [
            base_dir / ".env",
            base_dir.parent / ".env",
            Path("/home/user/.env")
        ]
        for c in candidates:
            if c.exists():
                env_path = str(c)
                break

    if env_path and os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'").strip('"')
                    os.environ[key] = val


# Automatically load .env on import
load_env_file()

# Default permanent configuration variables
DEFAULT_AFFILIATE_NETWORK = os.getenv("AFFILIATE_NETWORK", "travelpayouts")
DEFAULT_MARKER_ID = os.getenv("TRAVELPAYOUTS_MARKER", "760438")
DEFAULT_SUB_ID = os.getenv("AFFILIATE_SUB_ID", "aeroscrape_web")
