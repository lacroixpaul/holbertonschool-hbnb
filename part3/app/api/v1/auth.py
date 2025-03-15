from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade


api = Namespace('auth', description='Authentication operations')

# Model for input validation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        
        # Authenticate the user using the facade
        user = facade.authenticate_user(credentials['email'], credentials['password'])
        
        if not user:
            return {'error': 'Invalid credentials'}, 401
            
        # Create a JWT token
        access_token = create_access_token(identity={'id': str(user.id), 'is_admin': user.is_admin})
        
        return {'access_token': access_token}, 200
