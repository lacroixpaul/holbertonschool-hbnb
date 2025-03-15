import unittest
import json

from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models.user import User

class TestUserAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.client = cls.app.test_client()
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_create_valid_user(self):
        """
        Teste la création d'un utilisateur valide via l'API.
        Vérifie que le mot de passe est hashé et n'est pas renvoyé dans la réponse.
        """
        user_data = {
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'email': 'alice@example.com',
            'password': 'secret'
        }
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
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'admin@example.com',
            'password': 'adminpassword',
            'is_admin': True
        }
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

        with self.app.app_context():
            created_user = db.session.get(User, data['id'])
            self.assertIsNotNone(created_user)
            self.assertTrue(created_user.is_admin)

    def test_05_create_amenity_by_admin(self):
        """
        Teste la création d'une amenity par un administrateur.
        Vérifie que l'amenity est correctement créée lorsque l'admin a les privilèges.
        """
        amenity_data = {
            'name': 'Pool'
        }

        admin_data = {
            'first_name': 'Admin',
            'last_name': 'User',
            'email': 'adm@example.com',
            'password': 'adminpass',
            'is_admin': True
        }
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

    def test_06_update_amenity_by_admin(self):
        """
        Teste la mise à jour d'une amenity par un administrateur.
        Vérifie que l'amenity est correctement mise à jour lorsque l'admin a les privilèges.
        """
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'Amenity',
            'email': 'admin_amenity@example.com',
            'password': 'adminpass',
            'is_admin': True
        }
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
        login_data = {
            'email': 'admin_amenity@example.com',
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
        amenity_data = {
            'name': 'Jacuzzi'
        }
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        self.assertEqual(create_response.status_code, 201)
        created_amenity = create_response.get_json()
        amenity_id = created_amenity['id']
        update_data = {
            'name': 'Luxury Jacuzzi'
        }
        update_response = self.client.put(
            f'/api/v1/amenities/{amenity_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )        
        self.assertEqual(update_response.status_code, 200)
        update_result = update_response.get_json()
        self.assertIn('message', update_result)
        self.assertEqual(update_result['message'], 'Amenity updated successfully')
        with self.app.app_context():
            from app.models.amenity import Amenity
            updated_amenity = db.session.get(Amenity, amenity_id)
            self.assertEqual(updated_amenity.name, 'Luxury Jacuzzi')

    def test_07_create_amenity_by_regular_user(self):
        """
        Teste la création d'une amenity par un utilisateur régulier (non-admin).
        Vérifie que l'API refuse la création avec un code 403.
        """
        amenity_data = {
            'name': 'Wifi'
        }

        # Créer un utilisateur régulier (non-admin)
        regular_user_data = {
            'first_name': 'Regular',
            'last_name': 'User',
            'email': 'regular@example.com',
            'password': 'userpass',
            'is_admin': False
        }
        with self.app.app_context():
            regular_user = User(
                first_name=regular_user_data['first_name'],
                last_name=regular_user_data['last_name'],
                email=regular_user_data['email'],
                is_admin=regular_user_data['is_admin']
            )
            regular_user.hash_password(regular_user_data['password'])
            db.session.add(regular_user)
            db.session.commit()

        # Se connecter avec l'utilisateur régulier
        login_data = {
            'email': 'regular@example.com',
            'password': 'userpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.get_json()
        token = login_data.get('access_token')

        # Tenter de créer une amenity avec l'utilisateur régulier
        response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )

        # Vérifier que la requête est refusée avec un code 403
        data = response.get_json()
        self.assertEqual(response.status_code, 403)
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Admin privileges required')

    def test_08_update_amenity_by_regular_user(self):
        """
        Teste la mise à jour d'une amenity par un utilisateur régulier (non-admin).
        Crée d'abord une amenity avec un admin, puis tente de la modifier avec un utilisateur régulier.
        """
        # Créer un admin pour créer l'amenity
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'Test',
            'email': 'admin_test@example.com',
            'password': 'adminpass',
            'is_admin': True
        }
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
        
        # Se connecter avec l'admin
        login_data = {
            'email': 'admin_test@example.com',
            'password': 'adminpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        admin_token = login_response.get_json().get('access_token')
        
        # Créer une amenity avec l'admin
        amenity_data = {
            'name': 'Breakfast'
        }
        create_response = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        self.assertEqual(create_response.status_code, 201)
        amenity_id = create_response.get_json()['id']
        
        # Créer un utilisateur régulier
        regular_data = {
            'first_name': 'Regular',
            'last_name': 'Updater',
            'email': 'regular_updater@example.com',
            'password': 'regularpass',
            'is_admin': False
        }
        with self.app.app_context():
            regular = User(
                first_name=regular_data['first_name'],
                last_name=regular_data['last_name'],
                email=regular_data['email'],
                is_admin=regular_data['is_admin']
            )
            regular.hash_password(regular_data['password'])
            db.session.add(regular)
            db.session.commit()
        
        # Se connecter avec l'utilisateur régulier
        login_data = {
            'email': 'regular_updater@example.com',
            'password': 'regularpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        regular_token = login_response.get_json().get('access_token')
        
        # Tenter de mettre à jour l'amenity avec l'utilisateur régulier
        update_data = {
            'name': 'Premium Breakfast'
        }
        update_response = self.client.put(
            f'/api/v1/amenities/{amenity_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {regular_token}'}
        )
        
        # Vérifier que la requête est refusée
        self.assertEqual(update_response.status_code, 403)
        update_result = update_response.get_json()
        self.assertIn('error', update_result)
        self.assertEqual(update_result['error'], 'Admin privileges required')

    def test_09_get_amenities_without_auth(self):
        """
        Teste que n'importe qui peut lister ou voir les détails des amenities,
        sans nécessiter d'authentification.
        """
        # Créer d'abord une amenity avec un admin
        admin_data = {
            'first_name': 'Admin',
            'last_name': 'Viewer',
            'email': 'admin_viewer@example.com',
            'password': 'adminpass',
            'is_admin': True
        }
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
        
        login_data = {
            'email': 'admin_viewer@example.com',
            'password': 'adminpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        admin_token = login_response.get_json().get('access_token')
        
        # Créer quelques amenities
        amenity1 = {'name': 'Gym'}
        amenity2 = {'name': 'Parking'}
        
        self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity1),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        response2 = self.client.post(
            '/api/v1/amenities/',
            data=json.dumps(amenity2),
            content_type='application/json',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        amenity_id = response2.get_json()['id']
        
        # Tester la liste des amenities sans authentification
        list_response = self.client.get('/api/v1/amenities/')
        self.assertEqual(list_response.status_code, 200)
        amenities = list_response.get_json()
        self.assertIsInstance(amenities, list)
        self.assertGreaterEqual(len(amenities), 2)
        
        # Tester l'accès à une amenity spécifique sans authentification
        detail_response = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(detail_response.status_code, 200)
        amenity_data = detail_response.get_json()
        self.assertEqual(amenity_data['name'], 'Parking')

    def test_10_create_review(self):
        """
        Teste la création d'une review par un utilisateur.
        Vérifie que la review est correctement créée avec les données fournies.
        """
        # Créer deux utilisateurs: un propriétaire et un reviewer
        owner_data = {
            'first_name': 'Place',
            'last_name': 'Owner',
            'email': 'owner@example.com',
            'password': 'ownerpass'
        }
        reviewer_data = {
            'first_name': 'Review',
            'last_name': 'Writer',
            'email': 'reviewer@example.com',
            'password': 'reviewpass'
        }
        
        with self.app.app_context():
            # Créer les utilisateurs
            owner = User(
                first_name=owner_data['first_name'],
                last_name=owner_data['last_name'],
                email=owner_data['email']
            )
            owner.hash_password(owner_data['password'])
            
            reviewer = User(
                first_name=reviewer_data['first_name'],
                last_name=reviewer_data['last_name'],
                email=reviewer_data['email']
            )
            reviewer.hash_password(reviewer_data['password'])
            
            db.session.add(owner)
            db.session.add(reviewer)
            db.session.commit()
            
            owner_id = str(owner.id)
            reviewer_id = str(reviewer.id)
            
            # Créer un place qui appartient à owner
            from app.models.place import Place
            place = Place(
                title='Test Place',
                description='A place for testing',
                price=100.0,
                latitude=48.856614,
                longitude=2.3522219,
                owner_id=owner_id
            )
            db.session.add(place)
            db.session.commit()
            place_id = str(place.id)
        
        # Se connecter avec le reviewer
        login_data = {
            'email': 'reviewer@example.com',
            'password': 'reviewpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()['access_token']
        
        # Créer une review
        review_data = {
            'text': 'This is a great place!',
            'rating': 5,
            'user_id': reviewer_id,
            'place_id': place_id
        }
        
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(review_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['text'], 'This is a great place!')
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['user_id'], reviewer_id)
        self.assertEqual(data['place_id'], place_id)

    def test_11_owner_cannot_review_own_place(self):
        """
        Teste qu'un propriétaire ne peut pas créer une review pour son propre place.
        """
        # Créer un utilisateur propriétaire
        owner_data = {
            'first_name': 'Self',
            'last_name': 'Reviewer',
            'email': 'selfreview@example.com',
            'password': 'selfpass'
        }
        
        with self.app.app_context():
            # Créer l'utilisateur
            owner = User(
                first_name=owner_data['first_name'],
                last_name=owner_data['last_name'],
                email=owner_data['email']
            )
            owner.hash_password(owner_data['password'])
            db.session.add(owner)
            db.session.commit()
            owner_id = str(owner.id)
            
            # Créer un place qui appartient à l'owner
            from app.models.place import Place
            place = Place(
                title='Self Review Place',
                description='A place for self-review testing',
                price=120.0,
                latitude=40.7128,
                longitude=-74.0060,
                owner_id=owner_id
            )
            db.session.add(place)
            db.session.commit()
            place_id = str(place.id)
        
        # Se connecter avec le propriétaire
        login_data = {
            'email': 'selfreview@example.com',
            'password': 'selfpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        self.assertEqual(login_response.status_code, 200)
        token = login_response.get_json()['access_token']
        
        # Tenter de créer une review pour son propre place
        review_data = {
            'text': 'My place is amazing!',
            'rating': 5,
            'user_id': owner_id,
            'place_id': place_id
        }
        
        response = self.client.post(
            '/api/v1/reviews/',
            data=json.dumps(review_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Vérifier que la création est refusée
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'You cannot review your own place')

    def test_12_update_review(self):
        """
        Teste la mise à jour d'une review par son auteur.
        """
        # Créer un propriétaire et un reviewer
        owner_data = {
            'first_name': 'Update',
            'last_name': 'Owner',
            'email': 'update_owner@example.com',
            'password': 'ownerpass'
        }
        reviewer_data = {
            'first_name': 'Update',
            'last_name': 'Reviewer',
            'email': 'update_reviewer@example.com',
            'password': 'reviewpass'
        }
        
        with self.app.app_context():
            # Créer les utilisateurs
            owner = User(
                first_name=owner_data['first_name'],
                last_name=owner_data['last_name'],
                email=owner_data['email']
            )
            owner.hash_password(owner_data['password'])
            
            reviewer = User(
                first_name=reviewer_data['first_name'],
                last_name=reviewer_data['last_name'],
                email=reviewer_data['email']
            )
            reviewer.hash_password(reviewer_data['password'])
            
            db.session.add(owner)
            db.session.add(reviewer)
            db.session.commit()
            
            owner_id = str(owner.id)
            reviewer_id = str(reviewer.id)
            
            # Créer un place
            from app.models.place import Place
            place = Place(
                title='Update Review Place',
                description='A place for update review testing',
                price=130.0,
                latitude=51.5074,
                longitude=-0.1278,
                owner_id=owner_id
            )
            db.session.add(place)
            db.session.commit()
            place_id = str(place.id)
            
            # Créer une review
            from app.models.review import Review
            review = Review(
                text='Initial review text',
                rating=4,
                user_id=reviewer_id,
                place_id=place_id
            )
            db.session.add(review)
            db.session.commit()
            review_id = str(review.id)
        
        # Se connecter avec le reviewer
        login_data = {
            'email': 'update_reviewer@example.com',
            'password': 'reviewpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        
        # Mettre à jour la review
        update_data = {
            'text': 'Updated review text',
            'rating': 3,
            'user_id': reviewer_id,
            'place_id': place_id
        }
        
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Vérifier la mise à jour
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Review updated successfully')
        
        # Vérifier que les données ont bien été mises à jour
        get_response = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(get_response.status_code, 200)
        review_data = get_response.get_json()
        self.assertEqual(review_data['text'], 'Updated review text')
        self.assertEqual(review_data['rating'], 3)

    def test_13_another_user_cannot_update_review(self):
        """
        Teste qu'un utilisateur ne peut pas modifier la review d'un autre utilisateur.
        """
        # Créer un propriétaire, un reviewer et un autre utilisateur
        owner_data = {
            'first_name': 'Another',
            'last_name': 'Owner',
            'email': 'another_owner@example.com',
            'password': 'ownerpass'
        }
        reviewer_data = {
            'first_name': 'Original',
            'last_name': 'Reviewer',
            'email': 'original_reviewer@example.com',
            'password': 'reviewpass'
        }
        other_user_data = {
            'first_name': 'Other',
            'last_name': 'User',
            'email': 'other_user@example.com',
            'password': 'otherpass'
        }
        
        with self.app.app_context():
            # Créer les utilisateurs
            owner = User(
                first_name=owner_data['first_name'],
                last_name=owner_data['last_name'],
                email=owner_data['email']
            )
            owner.hash_password(owner_data['password'])
            
            reviewer = User(
                first_name=reviewer_data['first_name'],
                last_name=reviewer_data['last_name'],
                email=reviewer_data['email']
            )
            reviewer.hash_password(reviewer_data['password'])
            
            other_user = User(
                first_name=other_user_data['first_name'],
                last_name=other_user_data['last_name'],
                email=other_user_data['email']
            )
            other_user.hash_password(other_user_data['password'])
            
            db.session.add(owner)
            db.session.add(reviewer)
            db.session.add(other_user)
            db.session.commit()
            
            owner_id = str(owner.id)
            reviewer_id = str(reviewer.id)
            
            # Créer un place
            from app.models.place import Place
            place = Place(
                title='No Modify Place',
                description='A place for testing no modification',
                price=140.0,
                latitude=35.6762,
                longitude=139.6503,
                owner_id=owner_id
            )
            db.session.add(place)
            db.session.commit()
            place_id = str(place.id)
            
            # Créer une review par le reviewer original
            from app.models.review import Review
            review = Review(
                text='Original review that should not be modified by others',
                rating=5,
                user_id=reviewer_id,
                place_id=place_id
            )
            db.session.add(review)
            db.session.commit()
            review_id = str(review.id)
        
        # Se connecter avec l'autre utilisateur
        login_data = {
            'email': 'other_user@example.com',
            'password': 'otherpass'
        }
        login_response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        token = login_response.get_json()['access_token']
        
        # Tenter de modifier la review
        update_data = {
            'text': 'This review has been hijacked!',
            'rating': 1,
            'user_id': reviewer_id,  # On conserve l'ID du reviewer original
            'place_id': place_id
        }
        
        response = self.client.put(
            f'/api/v1/reviews/{review_id}',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        # Vérifier que la modification est refusée
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], 'Forbidden: You are not the owner of this review')
        
        # Vérifier que la review n'a pas été modifiée
        get_response = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(get_response.status_code, 200)
        review_data = get_response.get_json()
        self.assertEqual(review_data['text'], 'Original review that should not be modified by others')
        self.assertEqual(review_data['rating'], 5)


if __name__ == '__main__':
    unittest.main()
