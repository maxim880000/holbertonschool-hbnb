from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from app.services import facade

api = Namespace('users', description='Operations on users')

user_model = api.model('User', {
    'id':         fields.String(readonly=True, description='User unique identifier'),
    'email':      fields.String(required=True, description='User email'),
    'first_name': fields.String(description='First name'),
    'last_name':  fields.String(description='Last name'),
    'is_admin':   fields.Boolean(description='Admin flag'),
    'created_at': fields.String(readonly=True),
    'updated_at': fields.String(readonly=True),
})

create_user_model = api.model('UserCreate', {
    'email':      fields.String(required=True),
    'password':   fields.String(required=True, description='Plain-text, sera hashé avant stockage'),
    'first_name': fields.String(required=True),
    'last_name':  fields.String(required=True),
})

update_user_model = api.model('UserUpdate', {
    'first_name': fields.String(),
    'last_name':  fields.String(),
    'password':   fields.String(description='Nouveau mot de passe, sera hashé avant stockage'),
})

login_model = api.model('UserLogin', {
    'email':    fields.String(required=True),
    'password': fields.String(required=True),
})

@api.route('/me')
class UserMe(Resource):
    @jwt_required()
    def get(self):
        identity = get_jwt()
        return {'user': identity}, 200

@api.route('/')
class UserList(Resource):
    @api.marshal_list_with(user_model)
    def get(self):
        users = facade.get_users()
        return [u.to_dict() for u in users], 200

    @jwt_required(optional=True)
    @api.expect(create_user_model)
    @api.response(201, 'User created', user_model)
    @api.response(400, 'Bad request')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'Email already exists')
    def post(self):
        current = get_jwt() or {}
        is_admin = current.get('is_admin', False)
        data = api.payload or {}
        if not facade.get_users():
            data['is_admin'] = True
        else:
            if not is_admin:
                return {'error': 'Admin privileges required'}, 403
            data.setdefault('is_admin', False)
        try:
            user = facade.create_user(data)
        except ValueError as e:
            msg = str(e)
            if 'in use' in msg:
                return {'message': msg}, 409
            return {'message': msg}, 400
        return user.to_dict(), 201

@api.route('/login')
class UserLogin(Resource):
    @api.expect(login_model)
    def post(self):
        data = api.payload or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'message': 'email and password required'}, 400
        user = facade.get_user_by_email(email)
        if not user or not user.verify_password(password):
            return {'message': 'Invalid credentials'}, 401
        additional_claims = {'id': user.id, 'is_admin': user.is_admin}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return {'access_token': access_token}, 200

@api.route('/<string:user_id>')
@api.param('user_id', 'The user identifier')
class UserResource(Resource):
    @api.marshal_with(user_model)
    @api.response(404, 'User not found')
    def get(self, user_id):
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200

    @jwt_required()
    @api.expect(update_user_model)
    @api.response(200, 'User updated', user_model)
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'User not found')
    def put(self, user_id):
        current = get_jwt()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        data = api.payload or {}
        if 'email' in data:
            existing = facade.get_user_by_email(data['email'])
            if existing and existing.id != user_id:
                return {'error': 'Email already in use'}, 400
        try:
            user = facade.update_user(user_id, data)
        except ValueError as e:
            msg = str(e)
            if 'in use' in msg:
                return {'error': msg}, 400
            return {'error': msg}, 400
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200
@api.route('/me')
class UserMe(Resource):
    @jwt_required()
    def get(self):
        """Return current user info from JWT token"""
        identity = get_jwt()
        return {'user': identity}, 200
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required

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

login_model = api.model('UserLogin', {
    'email':    fields.String(required=True),
    'password': fields.String(required=True),
})


@api.route('/')
class UserList(Resource):

    @api.marshal_list_with(user_model)
    def get(self):
        """Return list of all users (password excluded)"""
        users = facade.get_users()
        return [u.to_dict() for u in users], 200

    @jwt_required(optional=True)
    @api.expect(create_user_model)
    @api.response(201, 'User created', user_model)
    @api.response(400, 'Bad request')
    @api.response(403, 'Admin privileges required')
    @api.response(409, 'Email already exists')
    def post(self):
        """Create a new user — password is hashed before storage"""
        current = get_jwt() or {}
        is_admin = current.get('is_admin', False)

        data = api.payload or {}
        # First user can bootstrap the system as an admin
        if not facade.get_users():
            data['is_admin'] = True
        else:
            if not is_admin:
                return {'error': 'Admin privileges required'}, 403
            # Admin can explicitly set is_admin flag; default to False if not provided
            data.setdefault('is_admin', False)

        try:
            user = facade.create_user(data)
        except ValueError as e:
            msg = str(e)
            if 'in use' in msg:
                return {'message': msg}, 409
            return {'message': msg}, 400
        # to_dict() n'inclut pas le password — réponse sécurisée
        return user.to_dict(), 201


@api.route('/login')
class UserLogin(Resource):

    @api.expect(login_model)
    def post(self):
        """Authenticate a user and return a JWT access token."""
        data = api.payload or {}
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return {'message': 'email and password required'}, 400

        user = facade.get_user_by_email(email)
        if not user or not user.verify_password(password):
            return {'message': 'Invalid credentials'}, 401

        additional_claims = {'id': user.id, 'is_admin': user.is_admin}
        access_token = create_access_token(identity=user.id, additional_claims=additional_claims)
        return {'access_token': access_token}, 200


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

    @jwt_required()
    @api.expect(update_user_model)
    @api.response(200, 'User updated', user_model)
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update a user — password is re-hashed if provided"""
        current = get_jwt()
        if not current.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        data = api.payload or {}
        # Ensure updated email stays unique
        if 'email' in data:
            existing = facade.get_user_by_email(data['email'])
            if existing and existing.id != user_id:
                return {'error': 'Email already in use'}, 400

        try:
            user = facade.update_user(user_id, data)
        except ValueError as e:
            msg = str(e)
            if 'in use' in msg:
                return {'error': msg}, 400
            return {'error': msg}, 400
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200