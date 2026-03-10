from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt

from app.config import config

bcrypt = Bcrypt()


def create_app(config_name='development'):
    """Create and configure the Flask application.

    The more complex version from `dev` branch is used: it loads a
    configuration object, instantiates an API with its own documentation
    path, and registers the relevant namespaces.
    """
    app = Flask(__name__)

    # configuration
    app.config.from_object(config[config_name])

    # extensions
    bcrypt.init_app(app)

    # API setup
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/doc',  # Swagger UI séparé du préfixe API
    )

    # register namespaces (lazy imports to avoid circulars)
    from app.api.v1.users import api as users_ns
    api.add_namespace(users_ns, path='/api/v1/users')

    from app.api.v1.places import api as places_ns
    api.add_namespace(places_ns, path='/api/v1/places')

    from app.api.v1.amenities import api as amenities_ns
    api.add_namespace(amenities_ns, path='/api/v1/amenities')

    from app.api.v1.reviews import api as reviews_ns
    api.add_namespace(reviews_ns, path='/api/v1/reviews')

    return app
