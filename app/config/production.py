"""
Production Configuration
"""

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Configuration for production deployment."""

    DEBUG = False