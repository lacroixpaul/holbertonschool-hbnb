from app import db
Base = db.Model

from .user import User
from .place import Place
from .place_amenity import place_amenity
from .review import Review
from .amenity import Amenity
