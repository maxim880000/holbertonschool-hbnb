from flask import Flask
from flask_restx import Api


def create_app():
    app = Flask(__name__)
    api = Api(app, version='1.0', title='HBnB API',
            description='HBnB Application API', doc='/api/v1/')

    # import and register namespaces
    from app.api.v1.users import api as users_ns
    api.add_namespace(users_ns, path='/api/v1/users')

    from app.api.v1.places import api as places_ns
    # On importe le namespace places depuis api/v1/places.py
    api.add_namespace(places_ns, path='/api/v1/places')
    # Tous les endpoints de places.py seront accessibles via /api/v1/places

    return app
