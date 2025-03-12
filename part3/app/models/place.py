from app import db
from .basemodel import BaseModel
from app.models.review import Review
from app.models.amenity import Amenity
from sqlalchemy.orm import validates

class Place(BaseModel):
    __tablename__ = 'places'

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    owner = db.relationship("User", backref="places")
    amenities = db.relationship("Amenity", secondary="place_amenity", backref="places")
    
    reviews = db.relationship(
        "Review",
        back_populates="place",
        cascade="all, delete-orphan",
        primaryjoin="Place.id == Review.place_id"
    )

    @validates('price')
    def validate_price(self, key, value):
        """Empêche d'avoir un prix négatif"""
        if value < 0:
            raise ValueError("Price must be a positive number")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        """Empêche une latitude hors des valeurs acceptables (-90 à 90)"""
        if not (-90 <= value <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        """Empêche une longitude hors des valeurs acceptables (-180 à 180)"""
        if not (-180 <= value <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return value

    def add_review(self, review):
        """Ajoute une review au lieu sans l'imposer en base de données."""
        if not isinstance(review, Review):
            raise TypeError("Expected a Review object")

        session = db.session.object_session(self) or db.session

        if review not in session:
            session.add(review)
            session.flush()

        with db.session.no_autoflush:
            if review not in self.reviews:
                self.reviews.append(review)


    def add_amenity(self, amenity):
        """Ajoute une amenity au lieu sans l'imposer en base de données."""
        if not isinstance(amenity, Amenity):
            raise TypeError("Expected an Amenity object")

        session = db.session.object_session(self) or db.session

        with db.session.no_autoflush:
            if amenity not in self.amenities:
                if amenity not in session:
                    session.add(amenity)
                    session.flush()
                self.amenities.append(amenity)


    def to_dict(self):
        """Convert Place object to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner_id': self.owner_id
        }

    def to_dict_list(self):
        """Convert Place object including owner, amenities, and reviews."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'owner': self.owner.to_dict(),
            'amenities': [amenity.to_dict() for amenity in self.amenities],
            'reviews': [review.to_dict() for review in self.reviews]
        }
