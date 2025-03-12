import unittest
from sqlalchemy.exc import IntegrityError
from app.models import Review, Place, User
from app.test_models.test_database import setup_in_memory_db

class TestReviewModel(unittest.TestCase):

    def setUp(self):
        """Initialise une base de données en mémoire pour chaque test."""
        self.Session, self.engine = setup_in_memory_db()
        self.session = self.Session()

        # Création d'un utilisateur et d'un lieu pour les reviews
        self.user = User(first_name="Alice", last_name="Smith", email="alice.smith@example.com")
        self.user.hash_password("securepassword")
        self.session.add(self.user)
        self.session.commit()

        self.place = Place(
            title="Cozy Apartment",
            description="A nice place to stay",
            price=100,
            latitude=37.7749,
            longitude=-122.4194,
            owner=self.user
        )
        self.session.add(self.place)
        self.session.commit()

    def tearDown(self):
        """Ferme la session et détruit la base après chaque test."""
        self.session.close()
        self.engine.dispose()

    def test_review_creation(self):
        """Test la création d'une review valide."""
        review = Review(text="Amazing place!", rating=5, place=self.place, user=self.user)
        self.session.add(review)
        self.session.commit()

        retrieved_review = self.session.query(Review).filter_by(text="Amazing place!").first()
        self.assertIsNotNone(retrieved_review)
        self.assertEqual(retrieved_review.text, "Amazing place!")
        self.assertEqual(retrieved_review.rating, 5)
        self.assertEqual(retrieved_review.place_id, self.place.id)
        self.assertEqual(retrieved_review.user_id, self.user.id)

    def test_review_missing_fields(self):
        """Test qu'une review ne peut pas être créée sans champs obligatoires."""
        with self.assertRaises(IntegrityError):
            review = Review(rating=5, place=self.place, user=self.user)  # Sans texte
            self.session.add(review)
            self.session.commit()
        self.session.rollback()

        with self.assertRaises(IntegrityError):
            review = Review(text="Great!", place=self.place, user=self.user)  # Sans rating
            self.session.add(review)
            self.session.commit()
        self.session.rollback()

    def test_review_invalid_rating(self):
        """Test qu'une review ne peut pas avoir un rating en dehors de 1 à 5."""
        with self.assertRaises(ValueError) as context:
            review = Review(text="Bad experience", rating=6, place=self.place, user=self.user)
            self.session.add(review)
            self.session.commit()
        self.assertEqual(str(context.exception), "Rating must be between 1 and 5")

        with self.assertRaises(ValueError) as context:
            review = Review(text="Terrible", rating=0, place=self.place, user=self.user)
            self.session.add(review)
            self.session.commit()
        self.assertEqual(str(context.exception), "Rating must be between 1 and 5")

    def test_review_update(self):
        """Test la mise à jour d'une review existante."""
        review = Review(text="Nice stay!", rating=4, place=self.place, user=self.user)
        self.session.add(review)
        self.session.commit()

        review.text = "Great experience!"
        review.rating = 5
        self.session.commit()

        retrieved_review = self.session.query(Review).filter_by(id=review.id).first()
        self.assertEqual(retrieved_review.text, "Great experience!")
        self.assertEqual(retrieved_review.rating, 5)

    def test_review_deletion(self):
        """Test la suppression d'une review."""
        review = Review(text="Will come again!", rating=5, place=self.place, user=self.user)
        self.session.add(review)
        self.session.commit()

        self.session.delete(review)
        self.session.commit()

        deleted_review = self.session.query(Review).filter_by(text="Will come again!").first()
        self.assertIsNone(deleted_review)

if __name__ == "__main__":
    unittest.main()
