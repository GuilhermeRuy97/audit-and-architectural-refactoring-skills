import os
import warnings

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

if SECRET_KEY == "dev-insecure-change-me":
    warnings.warn(
        "SECRET_KEY not set — using insecure development default. "
        "Set the SECRET_KEY environment variable before deploying.",
        stacklevel=2,
    )
