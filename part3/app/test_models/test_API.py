import unittest
import json
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
        # Vérifie que la création est réussie (code 201)
        self.assertEqual(response.status_code, 201)
        # Analyse la réponse JSON
        data = response.get_json()
        # On s'attend à recevoir un ID et un message de succès
        self.assertIn('id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'User successfully created')
        # Le mot de passe ne doit pas apparaître dans la réponse
        self.assertNotIn('password', data)

    def test_02_authentication(self):
        """
        Teste l'authentification d'un utilisateur via l'API.
        Crée un utilisateur dans la base et tente de se connecter via l'endpoint auth.
        """
        # Créer un utilisateur directement dans la base de données
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

        # Préparer les données pour l'authentification
        login_data = {
            'email': 'bob@example.com',
            'password': 'buildit'
        }
        # Envoyer une requête POST vers l'endpoint d'authentification
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        # Vérifier que la réponse a un statut 200
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Vérifier qu'un token d'accès est retourné dans la réponse
        self.assertIn('access_token', data)
        # Optionnel : vérifier que le token n'est pas vide
        self.assertTrue(len(data['access_token']) > 0)

if __name__ == '__main__':
    unittest.main()
