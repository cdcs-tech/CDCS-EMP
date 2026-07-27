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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

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