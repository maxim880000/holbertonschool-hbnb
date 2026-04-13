"""
Amenity endpoints — /api/v1/amenities
Supported operations: POST, GET (list + detail), PUT
DELETE is intentionally omitted in Part 2.
"""
from flask_restx import Namespace, Resource, fields
from app.services.facade import HBnBFacade

api = Namespace("amenities", description="Amenity management operations")

# Shared facade instance (imported from app context in production;
# instantiated here for clarity — see app/__init__.py for the real wiring).
facade = HBnBFacade()

# ------------------------------------------------------------------ #
#  flask-restx models (used for request parsing & Swagger docs)       #
# ------------------------------------------------------------------ #
amenity_input_model = api.model(
    "AmenityInput",
    {
        "name": fields.String(
            required=True,
            description="Name of the amenity (max 50 chars)",
            example="Wi-Fi",
        ),
    },
)

amenity_output_model = api.model(
    "Amenity",
    {
        "id": fields.String(description="Unique identifier"),
        "name": fields.String(description="Amenity name"),
        "created_at": fields.String(description="ISO 8601 creation timestamp"),
        "updated_at": fields.String(description="ISO 8601 last-update timestamp"),
    },
)


# ------------------------------------------------------------------ #
#  Collection resource  →  /api/v1/amenities/                         #
# ------------------------------------------------------------------ #
@api.route("/")
class AmenityList(Resource):
    """Handles listing all amenities and creating a new one."""

    @api.marshal_list_with(amenity_output_model)
    def get(self):
        """Retrieve the full list of amenities."""
        amenities = facade.get_all_amenities()
        return [a.to_dict() for a in amenities], 200

    @api.expect(amenity_input_model, validate=True)
    @api.response(201, "Amenity successfully created.")
    @api.response(400, "Validation error.")
    def post(self):
        """Create a new amenity."""
        data = api.payload

        # Validate required fields
        if not data or not data.get("name"):
            api.abort(400, "Field 'name' is required.")

        try:
            amenity = facade.create_amenity(data)
        except ValueError as exc:
            api.abort(400, str(exc))

        return amenity.to_dict(), 201


# ------------------------------------------------------------------ #
#  Individual resource  →  /api/v1/amenities/<amenity_id>             #
# ------------------------------------------------------------------ #
@api.route("/<string:amenity_id>")
@api.param("amenity_id", "The unique amenity identifier")
class AmenityResource(Resource):
    """Handles retrieving and updating a single amenity."""

    @api.marshal_with(amenity_output_model)
    @api.response(404, "Amenity not found.")
    def get(self, amenity_id: str):
        """Retrieve a single amenity by its ID."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity {amenity_id} not found.")
        return amenity.to_dict(), 200

    @api.expect(amenity_input_model, validate=True)
    @api.response(200, "Amenity successfully updated.")
    @api.response(400, "Validation error.")
    @api.response(404, "Amenity not found.")
    def put(self, amenity_id: str):
        """Update an existing amenity."""
        data = api.payload

        if not data:
            api.abort(400, "Request body must not be empty.")

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity {amenity_id} not found.")

        try:
            updated = facade.update_amenity(amenity_id, data)
        except ValueError as exc:
            api.abort(400, str(exc))

        return updated.to_dict(), 200
