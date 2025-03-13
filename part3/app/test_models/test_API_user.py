import unittest
import json

from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models.user import User

class TestUserAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Utilise la configuration de base
        cls.app = create_app()  # ou create_app('config.Config') si ta config de base s'appelle ainsi
        cls.app.config['TESTING'] = True  # Active le mode test
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Nettoyage complet de la DB après l'exécution de tous les tests
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_create_valid_user(self):
        """
        Teste la création d'un utilisateur valide via l'API.
        Vérifie que le mot de passe est hashé et n'est pas renvoyé dans la réponse.
        """
        # Données valides avec mot de passe
        user_data = {
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'email': 'alice@example.com',
            'password': 'secret'
        }
        # Envoi d'une requête POST vers l'endpoint de création d'utilisateur
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(user_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User successfully created')
        self.assertNotIn('password', data)

    def test_02_authentication(self):
        """
        Teste l'authentification d'un utilisateur via l'API.
        Crée un utilisateur dans la base et tente de se connecter via l'endpoint auth.
        """
        user_data = {
            'first_name': 'Bob',
            'last_name': 'Builder',
            'email': 'bob@example.com',
            'password': 'buildit'
        }
        with self.app.app_context():
            user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email']
            )
            user.hash_password(user_data['password'])
            db.session.add(user)
            db.session.commit()
        login_data = {
            'email': 'bob@example.com',
            'password': 'buildit'
        }
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        self.assertTrue(len(data['access_token']) > 0)

    def test_02_get_user_by_id(self):
        """Test récupération utilisateur par ID"""
        with self.app.app_context():
            user = User(first_name='John', last_name='Doe', email='john@example.com')
            user.hash_password('secret')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], user_id)
        self.assertEqual(data['email'], 'john@example.com')

    def test_03_update_user_valid(self):
        """
        Teste la mise à jour valide des informations d'un utilisateur.
        Vérifie que les informations sont mises à jour sauf email et mot de passe qui sont protégés.
        """
        user_data = {
            'first_name': 'Charlie',
            'last_name': 'Chaplin',
            'email': 'charlie@example.com',
            'password': 'funnywalk'
        }
        with self.app.app_context():
            user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email']
            )
            user.hash_password(user_data['password'])
            db.session.add(user)
            db.session.commit()
            user_id = str(user.id)

        login_data = {
            'email': 'charlie@example.com',
            'password': 'funnywalk'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json().get('access_token')
        self.assertIsNotNone(token)

        update_data = {
            'first_name': 'Charles',
            'last_name': 'Chaplin Jr'
        }
        update_response = self.client.put(
            f'/api/v1/users/{user_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(update_response.status_code, 200)
        response_data = update_response.get_json()
        self.assertIn('message', response_data)
        self.assertEqual(response_data['message'], 'User details updated successfully')
        with self.app.app_context():
            updated_user = db.session.get(User, user_id)
            self.assertEqual(updated_user.first_name, 'Charles')
            self.assertEqual(updated_user.last_name, 'Chaplin Jr')

    def test_04_create_admin_user(self):
        """
        Teste la création d'un utilisateur admin via l'API.
        Vérifie que l'attribut 'is_admin' est bien défini à True pour un utilisateur admin.
        """
        # Données valides pour un utilisateur admin
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@example.com',
            'password': 'adminpassword',
            'is_admin': True  # Spécifie que l'utilisateur est un admin
        }
        # Envoi d'une requête POST vers l'endpoint de création d'utilisateur
        response = self.client.post(
            '/api/v1/users/',
            data=json.dumps(admin_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User successfully created')

        # Vérification dans la base de données que l'utilisateur a bien été créé en tant qu'admin
        with self.app.app_context():
            created_user = db.session.get(User, data['id'])
            self.assertIsNotNone(created_user)
            self.assertTrue(created_user.is_admin)  # L'attribut 'is_admin' doit être True

    def test_05_create_amenity_by_admin(self):
        """
        Teste la création d'une amenity par un administrateur.
        Vérifie que l'amenity est correctement créée lorsque l'admin a les privilèges.
        """
        # Données d'amenity à créer
        amenity_data = {
            'name': 'Pool'
        }

        # Création d'un admin pour l'authentification
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'adm@example.com',
            'password': 'adminpass',
            'is_admin': True
        }
        # Enregistrement de l'admin dans la base de données
        with self.app.app_context():
            admin = User(
                first_name=admin_data['first_name'],
                last_name=admin_data['last_name'],
                email=admin_data['email'],
                is_admin=admin_data['is_admin']
            )
            admin.hash_password(admin_data['password'])
            db.session.add(admin)
            db.session.commit()

        # Connexion de l'admin pour récupérer le token
        login_data = {
            'email': 'adm@example.com',
            'password': 'adminpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.get_json()
        token = login_data.get('access_token')

        # Création de l'amenity avec le token d'admin
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )

        data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', data)
        self.assertIn('name', data)
 
if __name__ == '__main__':
    unittest.main()
