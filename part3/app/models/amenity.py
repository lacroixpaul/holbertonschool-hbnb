from app import db
from .basemodel import BaseModel

class Amenity(BaseModel):
    __tablename__ = 'amenities'  # ✅ Define the table name

    name = db.Column(db.String(50), nullable=False, unique=True)  # ✅ Unique amenity name

    def to_dict(self):
        """Convert Amenity object to dictionary."""
        return {
            'id': self.id,
            'name': self.name
        }
