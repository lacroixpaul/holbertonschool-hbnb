from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from app.models.user import User
from app.services import facade
from werkzeug.security import generate_password_hash

api = Namespace('admin', description='Admin operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Name of the amenity')
})

@api.route('/users/')
class AdminUserCreate(Resource):
    @jwt_required()
    def post(self):
        """Create a new user (only for admins)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        user_data = request.json
        email = user_data.get('email')
        if not email:
            return {'error': 'Email is required'}, 400
        if facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400
        password = user_data.get('password')
        if not password:
            return {'error': 'Password is required'}, 400
        hashed_password = generate_password_hash(password)
        try:
            new_user = facade.create_user({
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'email': email,
                'password': hashed_password
            })
            return {'id': new_user.id, 'message': 'User successfully created'}, 201
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/users/<user_id>')
class AdminUserModify(Resource):
    @jwt_required()
    def put(self, user_id):
        """Modify an existing user (only for admins)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        data = request.json
        email = data.get('email')
        password = data.get('password')

        if email:
            existing_user = facade.get_user_by_email(email)
            if existing_user and existing_user.id != user_id:
                return {'error': 'Email already in use'}, 400

        if password:
            hashed_password = generate_password_hash(password)
        else:
            hashed_password = None

        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        try:
            updated_data = {
                'first_name': data.get('first_name', user.first_name),
                'last_name': data.get('last_name', user.last_name),
                'email': email or user.email,
                'password': hashed_password if password else user.password
            }
            updated_user = facade.update_user(user_id, updated_data)
            return {'id': updated_user.id, 'message': 'User successfully updated'}, 200
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/amenities/')
class AdminAmenityCreate(Resource):
    @jwt_required()
    @api.expect(amenity_model, validate=True)
    def post(self):
        """Create a new amenity (only for admins)"""
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        amenity_data = request.json
        name = amenity_data.get('name')
        existing_amenity = facade.get_amenity_by_name(name)
        if existing_amenity:
            return {'error': 'Amenity with this name already exists'}, 400
        try:
            new_amenity = facade.create_amenity(amenity_data)
            return {'id': new_amenity.id, 'name': new_amenity.name, 'message': 'Amenity successfully created'}, 201
        except Exception as e:
            return {'error': str(e)}, 400

@api.route('/amenities/<amenity_id>')
class AdminAmenityModify(Resource):
    @jwt_required()
    def put(self, amenity_id):
        current_user = get_jwt_identity()
        if not current_user.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        amenity_data = request.json  
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity not found'}, 404
        try:
            if 'name' in amenity_data:
                amenity.name = amenity_data['name']
            if 'description' in amenity_data:
                amenity.description = amenity_data.get('description', '')
            facade.update_amenity(amenity)
            return {'message': 'Amenity updated successfully'}, 200
        except Exception as e:
            return {'error': str(e)}, 400
