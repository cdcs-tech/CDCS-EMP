"""
CDCS Enterprise Management Platform (CDCS-EMP)

Base Configuration
"""

import os
from datetime import timedelta
from urllib.parse import quote_plus


class BaseConfig:
    """
    Base configuration shared by all environments.
    """

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "change-this-in-production",
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_SERVER = os.getenv("DB_SERVER", ".")
    DB_NAME = os.getenv("DB_NAME", "CDCS_EMP")
    DB_DRIVER = os.getenv(
        "DB_DRIVER",
        "ODBC Driver 18 for SQL Server",
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
        f"?driver={quote_plus(DB_DRIVER)}"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False

    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SECURE = False
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
