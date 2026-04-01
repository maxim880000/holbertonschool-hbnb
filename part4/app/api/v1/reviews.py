from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'id': fields.String(readonly=True),
    'rating': fields.Integer(description='Rating from 1 to 5'),
    'comment': fields.String(description='Review comment'),
    'place_id': fields.String(description='Place ID'),
    'user_id': fields.String(description='User ID'),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})

create_review_model = api.model('ReviewCreate', {
    'rating': fields.Integer(required=True, description='Rating 1-5'),
    'comment': fields.String(required=True),
    'place_id': fields.String(required=True),
    'user_id': fields.String(required=True),
})

update_review_model = api.model('ReviewUpdate', {
    'rating': fields.Integer(description='Rating 1-5'),
    'comment': fields.String(),
})


@api.route('/')
class ReviewList(Resource):

    @api.marshal_list_with(review_model)
    @api.response(200, 'List of reviews')
    def get(self):
        """Retrieve all reviews"""
        return [r.to_dict() for r in facade.get_all_reviews()], 200

    @jwt_required()
    @api.expect(create_review_model, validate=True)
    @api.response(201, 'Review created', review_model)
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User or place not found')
    def post(self):
        """Create a new review"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        payload = api.payload or {}
        if not is_admin and payload.get('user_id') != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            review = facade.create_review(payload)
        except ValueError as e:
            msg = str(e)
            if 'not found' in msg:
                return {'message': msg}, 404
            return {'message': msg}, 400
        return review.to_dict(), 201


@api.route('/<string:review_id>')
@api.param('review_id', 'The review identifier')
class ReviewResource(Resource):

    @api.marshal_with(review_model)
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')
        return review.to_dict(), 200

    @jwt_required()
    @api.expect(update_review_model, validate=True)
    @api.response(200, 'Review updated', review_model)
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            review = facade.update_review(review_id, api.payload)
        except ValueError as e:
            return {'message': str(e)}, 400
        if not review:
            api.abort(404, 'Review not found')
        return review.to_dict(), 200

    @jwt_required()
    @api.response(200, 'Review deleted')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        current = get_jwt()
        is_admin = current.get('is_admin', False)
        user_id = get_jwt_identity()

        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        if not is_admin and review.user.id != user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
@api.param('place_id', 'The place identifier')
class PlaceReviewList(Resource):

    @api.marshal_list_with(review_model)
    @api.response(200, 'Reviews for the place')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        return [r.to_dict() for r in facade.get_reviews_by_place(place_id)], 200
