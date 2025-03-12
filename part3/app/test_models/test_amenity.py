import unittest
from sqlalchemy.exc import IntegrityError
from app.models import Amenity
from app.test_models.test_database import setup_in_memory_db

class TestAmenity(unittest.TestCase):

    def setUp(self):
        """Initialise une base de données en mémoire pour chaque test."""
        self.Session, self.engine = setup_in_memory_db()
        self.session = self.Session()

    def tearDown(self):
        """Ferme la session et détruit la base après chaque test."""
        self.session.close()
        self.engine.dispose()

    def test_amenity_creation(self):
        """Test la création d'un amenity valide."""
        amenity = Amenity(name="Wi-Fi")
        self.session.add(amenity)
        self.session.commit()

        retrieved_amenity = self.session.query(Amenity).filter_by(name="Wi-Fi").first()
        self.assertIsNotNone(retrieved_amenity)
        self.assertEqual(retrieved_amenity.name, "Wi-Fi")

    def test_amenity_max_length(self):
        """Test qu'un nom d'amenity ne peut pas dépasser 50 caractères."""
        with self.assertRaises(ValueError) as context:
            amenity = Amenity(name="A" * 51)
            self.session.add(amenity)
            self.session.commit()
        self.assertEqual(str(context.exception), "Name must be at most 50 characters")

    def test_amenity_missing_field(self):
        """Test qu'un amenity ne peut pas être créé sans un nom."""
        with self.assertRaises(IntegrityError):
            amenity = Amenity()  # Pas de name
            self.session.add(amenity)
            self.session.commit()
        self.session.rollback()

    def test_amenity_unique_name(self):
        """Test qu'un amenity ne peut pas avoir un nom en double."""
        amenity1 = Amenity(name="Pool")
        amenity2 = Amenity(name="Pool")  # Même nom
        self.session.add(amenity1)
        self.session.commit()

        with self.assertRaises(IntegrityError):
            self.session.add(amenity2)
            self.session.commit()
        self.session.rollback()

    def test_amenity_update(self):
        """Test la mise à jour d'un amenity existant."""
        amenity = Amenity(name="Wi-Fi")
        self.session.add(amenity)
        self.session.commit()

        amenity.update({"name": "High-Speed Wi-Fi"})
        self.session.commit()

        retrieved_amenity = self.session.query(Amenity).filter_by(id=amenity.id).first()
        self.assertEqual(retrieved_amenity.name, "High-Speed Wi-Fi")

    def test_amenity_deletion(self):
        """Test la suppression d'un amenity."""
        amenity = Amenity(name="Gym")
        self.session.add(amenity)
        self.session.commit()

        self.session.delete(amenity)
        self.session.commit()

        deleted_amenity = self.session.query(Amenity).filter_by(name="Gym").first()
        self.assertIsNone(deleted_amenity)

if __name__ == "__main__":
    unittest.main()
