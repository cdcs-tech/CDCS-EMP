"""
Configuration Package
"""

from .development import DevelopmentConfig
from .testing import TestingConfig
from .production import ProductionConfig

config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
