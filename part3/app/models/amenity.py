from sqlalchemy.orm import validates
from app import db
from .basemodel import BaseModel

class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False, unique=True)

    @validates('name')
    def validate_name(self, key, value):
        """Empêche un nom trop long"""
        if len(value) > 50:
            raise ValueError("Name must be at most 50 characters")
        return value

    def update(self, data):
        """Mise à jour des données de l'amenity"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        """Convert Amenity object to dictionary."""
        return {
            'id': self.id,
            'name': self.name
        }
