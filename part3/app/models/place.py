from app import db
from .basemodel import BaseModel
from sqlalchemy.orm import relationship

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
