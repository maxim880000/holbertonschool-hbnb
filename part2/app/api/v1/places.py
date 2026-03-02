from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

# Modèle pour la validation des données en entrée (POST / PUT)
place_model = api.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'owner_id': fields.String(required=True, description='ID of the owner'),
    'amenities': fields.List(fields.String, required=False, description="List of amenities ID's")
})


@api.route('/')
class PlaceList(Resource):

    @api.expect(place_model, validate=True)
    @api.response(201, 'Place successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new place"""
        place_data = api.payload
        # api.payload contient le JSON envoyé par le client

        # Vérifie que la méthode de création de place est disponible dans la facade
        create_place_fn = getattr(facade, "create_place", None)
        if create_place_fn is None:
            # Fonctionnalité non encore implémentée côté service/facade
            return {'error': 'Place creation not implemented in service layer'}, 501

        try:
            new_place = create_place_fn(place_data)
            # La facade valide owner_id, price, latitude, longitude
            # et lève ValueError si quelque chose est invalide
        except ValueError as e:
            return {'message': str(e)}, 400
            # On retourne l'erreur avec un code 400 Bad Request

        return {
            'id': new_place.id,
            'title': new_place.title,
            'description': new_place.description,
            'price': new_place.price,
            'latitude': new_place.latitude,
            'longitude': new_place.longitude,
            'owner_id': new_place.owner.id
            # On retourne l'id du owner, pas l'objet entier
        }, 201

    @api.response(200, 'List of places retrieved successfully')
    def get(self):
        """Retrieve a list of all places"""
        if not hasattr(facade, 'get_all_places'):
            # La méthode n'est pas encore implémentée dans la facade
            return {'error': 'Listing places is not implemented in the service layer'}, 501
        places = facade.get_all_places()
        # get_all_places() retourne une liste de tous les objets Place

        return [
            {
                'id': place.id,
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude
                # La liste retourne uniquement les infos essentielles
                # Le détail complet est disponible via GET /<place_id>
            }
            for place in places
            # Compréhension de liste : transforme chaque Place en dict
        ], 200


@api.route('/<place_id>')
class PlaceResource(Resource):

    @api.response(200, 'Place details retrieved successfully')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get place details by ID including owner and amenities"""
        try:
            place = facade.get_place(place_id)
        except NotImplementedError:
            # Le service de récupération de lieu n'est pas encore implémenté
            return {'error': 'Place retrieval not implemented'}, 501
        # get_place() retourne None si le lieu n'existe pas

        if not place:
            api.abort(404, 'Place not found')

        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                # On retourne l'objet owner complet (pas juste l'id)
                # La consigne demande first_name, last_name, email
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name,
                'email': place.owner.email
            },
            'amenities': [
                # On retourne la liste des amenities complètes (id + name)
                {
                    'id': amenity.id,
                    'name': amenity.name
                }
                for amenity in place.amenities
                # Compréhension de liste : transforme chaque Amenity en dict
            ]
        }, 200

    @api.expect(place_model)
    @api.response(200, 'Place updated successfully')
    @api.response(404, 'Place not found')
    @api.response(400, 'Invalid input data')
    def put(self, place_id):
        """Update a place's information"""
        place_data = api.payload
        # api.payload contient le JSON envoyé par le client

        try:
            updated_place = facade.update_place(place_id, place_data)
            # update_place() retourne None si le lieu n'existe pas
        except ValueError as e:
            return {'error': str(e)}, 400

        if not updated_place:
            return {'error': 'Place not found'}, 404

        return {'message': 'Place updated successfully'}, 200
