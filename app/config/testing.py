"""
Testing Configuration
"""

import os
from urllib.parse import quote_plus

from .base import BaseConfig


class TestingConfig(BaseConfig):
    """
    SQL Server testing configuration.
    """

    TESTING = True

    WTF_CSRF_ENABLED = False

    DB_NAME = os.getenv(
        "TEST_DB_NAME",
        "CDCS_EMP_TEST",
    )

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://@{BaseConfig.DB_SERVER}/{DB_NAME}"
        f"?driver={quote_plus(BaseConfig.DB_DRIVER)}"
        "&trusted_connection=yes"
        "&TrustServerCertificate=yes"
    )
