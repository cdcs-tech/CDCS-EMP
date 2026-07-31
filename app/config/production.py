"""
Production Configuration
"""

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""

    DEBUG = False

    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
