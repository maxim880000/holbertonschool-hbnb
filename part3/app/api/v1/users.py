from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='Operations on users')

# Modèle de réponse — password volontairement ABSENT
# to_dict() ne le retourne pas, et on ne le déclare pas ici non plus
user_model = api.model('User', {
    'id':         fields.String(readonly=True, description='User unique identifier'),
    'email':      fields.String(required=True, description='User email'),
    'first_name': fields.String(description='First name'),
    'last_name':  fields.String(description='Last name'),
    'is_admin':   fields.Boolean(description='Admin flag'),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})

# Modèle de création — password requis, sera hashé par bcrypt côté modèle
create_user_model = api.model('UserCreate', {
    'email':      fields.String(required=True),
    'password':   fields.String(required=True, description='Plain-text, sera hashé avant stockage'),
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
})

# Modèle de mise à jour — password optionnel, sera re-hashé si fourni
update_user_model = api.model('UserUpdate', {
    'first_name': fields.String(),
    'last_name':  fields.String(),
    'password':   fields.String(description='Nouveau mot de passe, sera hashé avant stockage'),
})


@api.route('/')
class UserList(Resource):

    @api.marshal_list_with(user_model)
    def get(self):
        """Return list of all users (password excluded)"""
        users = facade.get_users()
        return [u.to_dict() for u in users], 200

    @api.expect(create_user_model)
    @api.response(201, 'User created', user_model)
    @api.response(400, 'Bad request')
    @api.response(409, 'Email already exists')
    def post(self):
        """Create a new user — password is hashed before storage"""
        data = api.payload
        try:
            user = facade.create_user(data)
        except ValueError as e:
            msg = str(e)
            if 'in use' in msg:
                return {'message': msg}, 409
            return {'message': msg}, 400
        # to_dict() n'inclut pas le password — réponse sécurisée
        return user.to_dict(), 201


@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):

    @api.marshal_with(user_model)
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Retrieve a user by ID (password excluded)"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        # to_dict() n'inclut pas le password — jamais exposé en GET
        return user.to_dict(), 200

    @api.expect(update_user_model)
    @api.response(200, 'User updated', user_model)
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update a user — password is re-hashed if provided"""
        data = api.payload
        user = facade.update_user(user_id, data)
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200