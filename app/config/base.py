"""
CDCS Enterprise Management Platform (CDCS-EMP)

Base Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration shared across all environments."""

    # ---------------------------------------------------------
    # General Application Settings
    # ---------------------------------------------------------
    APP_NAME = "CDCS Enterprise Management Platform"
    APP_VERSION = "0.1.0-alpha"

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "cdcs123456"
    )

    # ---------------------------------------------------------
    # Flask Settings
    # ---------------------------------------------------------
    DEBUG = False
    TESTING = False

    # ---------------------------------------------------------
    # SQLAlchemy Settings
    # ---------------------------------------------------------
    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
      raise RuntimeError(
        "DATABASE_URL environment variable is not configured."
    )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------------------------------------------------------
    # Session Settings
    # ---------------------------------------------------------
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

    # ---------------------------------------------------------
    # Upload Settings
    # ---------------------------------------------------------
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
