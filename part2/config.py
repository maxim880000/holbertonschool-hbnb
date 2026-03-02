import os


class Config:
    """Configuration de base partagée par tous les environnements."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration pour la suite de tests.
    TESTING=True désactive la gestion des erreurs de Flask pour que
    les exceptions remontent correctement dans les tests.
    """
    TESTING = True
    DEBUG = False


class ProductionConfig(Config):
    """Configuration pour la production.
    SECRET_KEY doit impérativement être défini dans l'environnement.
    """
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing':     TestingConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
