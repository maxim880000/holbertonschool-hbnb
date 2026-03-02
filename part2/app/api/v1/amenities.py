from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("amenities", description="Amenity management operations")

amenity_input_model = api.model(
    "AmenityInput",
    {
        "name": fields.String(required=True, description="Amenity name"),
        "description": fields.String(required=False, description="Amenity description"),
    },
)

amenity_output_model = api.model(
    "Amenity",
    {
        "id": fields.String(readonly=True),
        "name": fields.String(),
        "description": fields.String(),
        "created_at": fields.String(readonly=True),
        "updated_at": fields.String(readonly=True),
    },
)


@api.route("/")
class AmenityList(Resource):
    @api.marshal_list_with(amenity_output_model)
    def get(self):
        amenities = facade.get_all_amenities()
        return [amenity.to_dict() for amenity in amenities], 200

    @api.expect(amenity_input_model)
    @api.response(201, "Amenity created")
    @api.response(400, "Bad request")
    def post(self):
        data = api.payload or {}
        try:
            amenity = facade.create_amenity(data)
        except ValueError as exc:
            api.abort(400, str(exc))
        return amenity.to_dict(), 201


@api.route("/<string:amenity_id>")
@api.param("amenity_id", "Amenity identifier")
class AmenityResource(Resource):
    @api.marshal_with(amenity_output_model)
    @api.response(404, "Amenity not found")
    def get(self, amenity_id):
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, "Amenity not found")
        return amenity.to_dict(), 200

    @api.expect(amenity_input_model)
    @api.response(200, "Amenity updated")
    @api.response(404, "Amenity not found")
    @api.response(400, "Bad request")
    def put(self, amenity_id):
        data = api.payload or {}
        amenity = facade.update_amenity(amenity_id, data)
        if not amenity:
            api.abort(404, "Amenity not found")
        return amenity.to_dict(), 200
