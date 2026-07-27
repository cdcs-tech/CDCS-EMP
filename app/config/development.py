"""
Development Configuration
"""

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""

    DEBUG = True