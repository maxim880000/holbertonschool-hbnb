from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, jwt_required

from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'id': fields.String(readonly=True),
    'name': fields.String(required=True, description='Amenity name (max 50 chars)'),
    'description': fields.String(description='Optional description'),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})

create_amenity_model = api.model('AmenityCreate', {
    'name': fields.String(required=True),
    'description': fields.String(),
})

update_amenity_model = api.model('AmenityUpdate', {
    'name': fields.String(),
    'description': fields.String(),
})


@api.route('/')
class AmenityList(Resource):

    @api.marshal_list_with(amenity_model)
    @api.response(200, 'List of amenities')
    def get(self):
        """Retrieve all amenities"""
        return [a.to_dict() for a in facade.get_all_amenities()], 200

    @jwt_required()
    @api.expect(create_amenity_model, validate=True)
    @api.response(201, 'Amenity created', amenity_model)
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Create a new amenity"""
        current = get_jwt()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            amenity = facade.create_amenity(api.payload)
        except ValueError as e:
            return {'message': str(e)}, 400
        return amenity.to_dict(), 201


@api.route('/<string:amenity_id>')
@api.param('amenity_id', 'The amenity identifier')
class AmenityResource(Resource):

    @api.marshal_with(amenity_model)
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get an amenity by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity.to_dict(), 200

    @jwt_required()
    @api.expect(update_amenity_model, validate=True)
    @api.response(200, 'Amenity updated', amenity_model)
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    @api.response(400, 'Invalid input data')
    def put(self, amenity_id):
        """Update an amenity"""
        current = get_jwt()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        try:
            amenity = facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            return {'message': str(e)}, 400
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity.to_dict(), 200
