"""Application configuration classes."""
import os


class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


class TestingConfig:
    DEBUG = False
    TESTING = True
    SECRET_KEY = "test-secret-key"


class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
