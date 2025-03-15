from flask_jwt_extended import create_access_token
from app.persistence.repository import SQLAlchemyRepository
from app.persistence.user_repository import UserRepository
from app.persistence.place_repository import PlaceRepository
from app.persistence.review_repository import ReviewRepository
from app.persistence.amenity_repository import AmenityRepository
from app import db, bcrypt
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review

class HBnBFacade:
    def __init__(self):
        self.user_repository = UserRepository()
        self.place_repository = PlaceRepository()
        self.review_repository = ReviewRepository()
        self.amenity_repository = AmenityRepository()
    # USER
    def create_user(self, user_data):
        """Creates a new user and hashes the password before saving."""
        if 'password' not in user_data or not user_data['password']:
            raise ValueError("Password is required")

        password = user_data.pop('password')
        user = User(**user_data)
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user
        
    def get_users(self):
        return self.user_repository.get_all()

    def get_user(self, user_id):
        return self.user_repository.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repository.get_by_attribute('email', email)
    
    def update_user(self, user_id, user_data):
        self.user_repository.update(user_id, user_data)
    
    # AMENITY
    def create_amenity(self, amenity_data):
        """Creates a new amenity."""
        existing_amenity = self.amenity_repository.get_amenity_by_name(amenity_data['name'])
        if existing_amenity:
            raise ValueError("Amenity with this name already exists")

        amenity = Amenity(**amenity_data)
        db.session.add(amenity)
        db.session.commit()
        return amenity

    def get_amenity(self, amenity_id):
        """Retrieves a specific amenity."""
        return self.amenity_repository.get(amenity_id)

    def get_amenity_by_name(self, name):
        """Retrieve an amenity by its name using the AmenityRepository."""
        amenity = self.amenity_repository.get_amenity_by_name(name)
        return amenity

    def get_all_amenities(self):
        """Retrieves all amenities."""
        return self.amenity_repository.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        """Updates an amenity's details."""
        self.amenity_repository.update(amenity_id, amenity_data)

    # PLACE
    def create_place(self, place_data):
        """Creates a new place and associates it with a user."""
        user = self.user_repository.get(place_data['owner_id'])
        if not user:
            raise ValueError("Owner not found")

        place = Place(**place_data)
        db.session.add(place)
        db.session.commit()
        return place

    def get_places(self):
        """Retrieves all places."""
        return self.place_repository.get_all()

    def get_all_places(self):
        """Retrieve all places from the database."""
        return self.place_repository.get_all()

    def get_place_by_id(self, place_id):
        """Retrieves a specific place."""
        return self.place_repository.get(place_id)
    
    def update_place(self, place_id, place_data):
        """Updates a place's details in the database."""
        self.place_repository.update(place_id, place_data)

    # REVIEWS
    def create_review(self, review_data):
        """Creates a new review and associates it with a user and place."""
        user = self.user_repository.get(review_data['user_id'])
        place = self.place_repository.get(review_data['place_id'])

        if not user or not place:
            raise ValueError("Invalid User or Place ID")

        review = Review(**review_data)
        db.session.add(review)
        db.session.commit()
        return review

    def get_review(self, review_id):
        """Retrieves a specific review."""
        return self.review_repository.get(review_id)

    def get_all_reviews(self):
        """Retrieves all reviews."""
        return self.review_repository.get_all()

    def get_reviews_by_place(self, place_id):
        """Retrieves all reviews for a specific place."""
        return self.review_repository.get_reviews_by_place(place_id)

    def update_review(self, review_id, review_data):
        """Updates a review's details."""
        self.review_repository.update(review_id, review_data)

    def delete_review(self, review_id):
        """Deletes a review."""
        self.review_repository.delete(review_id)

    def authenticate_user(self, email, password):
        """Authenticate a user by email and password."""
        user = self.get_user_by_email(email)
        if user and user.verify_password(password):
            return user
        return None

    def get_review_by_place_and_user(self, place_id, user_id):
        """
        Retrieve a review by place_id and user_id
        """
        return Review.query.filter_by(place_id=place_id, user_id=user_id).first()
