import unittest
import requests
from app import db, create_app
from app.models import User
from flask_bcrypt import Bcrypt
import json
import jwt

bcrypt = Bcrypt()

def create_invalid_token():
    identity = {"sub": "fake_user_uuid", "is_admin": False}

    # Générer un token valide avec une clé incorrecte
    fake_token = jwt.encode(identity, "default_secret_key", algorithm="HS256")

    return fake_token

class TestUserEndpoint(unittest.TestCase):
    url = 'http://localhost:5000/api/v1/'
    headers = {'Content-Type': 'application/json'}
    user = None
    token = None

    @classmethod
    def setUpClass(cls):
        """Set up the database for testing within an application context."""
        cls.app = create_app()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down the database and application context."""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def test_01_create_user(self):
        user_data = {
            'first_name': 'test',
            'last_name': 'test',
            'email': 'test@gmail.com',
            'password': 'test'
        }
        response = requests.post(self.url + 'users/', json=user_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        user = User.query.filter_by(email='test@gmail.com').first()
        self.assertIsNotNone(user, "L'utilisateur devrait exister dans la base de données.")
        self.assertTrue(bcrypt.check_password_hash(user.password, user_data['password']), "Le mot de passe est stocké en clair !")
        TestUserEndpoint.user = response_data
        self.assertNotIn('password', response_data)

    def test_02_get_user(self):
        response = requests.get(self.url + f"users/{TestUserEndpoint.user['id']}")
        self.assertEqual(response.status_code, 200, "L'utilisateur n'est pas retrouvé.")
        response_data = response.json()
        self.assertNotIn('password', response_data)

    def test_03_test_login(self):
        login_data = {
            'email': 'test@gmail.com',
            'password': 'test'
        }
        response = requests.post(self.url + 'auth/login', json=login_data, headers=self.headers)
        
        response_data = response.json()
        self.assertEqual(response.status_code, 200, "La connexion n'a pas réussie.")
        self.assertIn('access_token', response_data, "L'access token est manquant dans la réponse.")
        
        TestUserEndpoint.token = response_data['access_token']
        TestUserEndpoint.headers['Authorization'] = f'Bearer {TestUserEndpoint.token}'
    
    def test_04_test_protected(self):
        headers = {"Authorization": f"Bearer {TestUserEndpoint.token}"}

        response = requests.get(self.url + 'auth/protected', headers=headers)

        self.assertEqual(response.status_code, 200, "Accès à l'endpoint protégé échoué.")

    def test_05_test_unauthorized(self):
        invalid_token = create_invalid_token()
        headers = {"Authorization": f"Bearer {invalid_token}"}

        response = requests.get(self.url + 'auth/protected', headers=headers)
        print(response.json())

        self.assertEqual(response.status_code, 422, "Accès à l'endpoint protégé a réussi alors que cela ne devrait pas.")

    def test_06_test_create_place_without_valid_token(self):
        print(TestUserEndpoint.user['id'])
        place_data = {
            "title": "Cozy Apartment",
            "description": "A nice place to stay",
            "price": 100.0,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner_id": TestUserEndpoint.user['id']
        }
        TestUserEndpoint.unauthenticated_headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {TestUserEndpoint.token}'}

        response = requests.post(self.url + 'places/', json=place_data, headers=TestUserEndpoint.unauthenticated_headers)
        print(response.json())


if __name__ == '__main__':
    unittest.main()
