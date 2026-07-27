"""
Testing Configuration
"""

from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Configuration used for automated tests."""

    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"