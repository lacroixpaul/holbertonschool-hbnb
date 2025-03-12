import unittest
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models import Base
from app.test_models.test_database import setup_in_memory_db

class TestUserModel(unittest.TestCase):

    def setUp(self):
        """Initialise une nouvelle base de données en mémoire pour chaque test."""
        self.Session, self.engine = setup_in_memory_db()
        self.session = self.Session()

    def tearDown(self):
        """Ferme la session et détruit la base après chaque test."""
        self.session.close()
        self.engine.dispose()

    def test_user_creation(self):
        """Test la création d'un utilisateur avec hachage du mot de passe."""
        user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
        user.hash_password("securepassword")
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(email="john.doe@example.com").first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.first_name, "John")
        self.assertEqual(retrieved_user.last_name, "Doe")
        self.assertEqual(retrieved_user.email, "john.doe@example.com")
        self.assertFalse(retrieved_user.is_admin)

        self.assertTrue(retrieved_user.verify_password("securepassword"))
        self.assertFalse(retrieved_user.verify_password("wrongpassword"))

    def test_user_max_length(self):
        """Test les limites de longueur des noms."""
        
        with self.assertRaises(ValueError) as context:
            user = User(first_name="A" * 51, last_name="Doe", email="john.doe@example.com")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), "First Name must be at most 50 characters")

        with self.assertRaises(ValueError) as context:
            user = User(first_name="John", last_name="B" * 51, email="john.doe@example.com")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), "Last Name must be at most 50 characters")

    def test_user_email(self):
        """Test les formats d'email invalides."""
        with self.assertRaises(ValueError) as context:
            user = User(first_name="John", last_name="Doe", email="john.doeexample.com")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), "Invalid email format")

    def test_user_required_fields(self):
        """Test les champs obligatoires."""

        with self.assertRaises(IntegrityError):
            user = User(first_name="John", last_name="Doe")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.session.rollback()

        with self.assertRaises(IntegrityError):
            user = User(first_name="John", email="john.doe@example.com")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.session.rollback()

        with self.assertRaises(IntegrityError):
            user = User(last_name="Doe", email="john.doe@example.com")
            user.hash_password("securepassword")
            self.session.add(user)
            self.session.commit()
        self.session.rollback()

    def test_user_update(self):
        """Test la mise à jour d'un utilisateur."""
        user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
        user.hash_password("securepassword")
        self.session.add(user)
        self.session.commit()

        user.first_name = "Jane"
        user.last_name = "Dupont"
        user.email = "jane.dupont@example.com"
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(email="jane.dupont@example.com").first()
        self.assertEqual(retrieved_user.first_name, "Jane")
        self.assertEqual(retrieved_user.last_name, "Dupont")

    def test_user_update_fail(self):
        """Test la mise à jour invalide d'un utilisateur."""
        user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
        user.hash_password("securepassword")
        self.session.add(user)
        self.session.commit()

        with self.assertRaises(ValueError) as context:
            user.first_name = "A" * 51
            self.session.commit()
        self.assertEqual(str(context.exception), "First Name must be at most 50 characters")

        with self.assertRaises(ValueError) as context:
            user.last_name = "B" * 51
            self.session.commit()
        self.assertEqual(str(context.exception), "Last Name must be at most 50 characters")

        with self.assertRaises(ValueError) as context:
            user.email = "john.doeexample.com"
            self.session.commit()
        self.assertEqual(str(context.exception), "Invalid email format")

    def test_password_verification(self):
        """Test la vérification du mot de passe haché."""
        user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
        user.hash_password("securepassword")
        self.session.add(user)
        self.session.commit()

        retrieved_user = self.session.query(User).filter_by(email="john.doe@example.com").first()
        self.assertTrue(retrieved_user.verify_password("securepassword"))
        self.assertFalse(retrieved_user.verify_password("wrongpassword"))

if __name__ == "__main__":
    unittest.main()
