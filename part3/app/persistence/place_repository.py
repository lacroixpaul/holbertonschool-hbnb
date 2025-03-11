from app.persistence.repository import SQLAlchemyRepository
from app.models.place import Place

class PlaceRepository(SQLAlchemyRepository):
    """Repository for handling Place-related database operations."""

    def __init__(self):
        super().__init__(Place)

    def get_places_by_owner(self, owner_id):
        """Retrieve all places owned by a specific user."""
        return self.model.query.filter_by(owner_id=owner_id).all()

    def get_places_by_price_range(self, min_price, max_price):
        """Retrieve places within a specified price range."""
        return self.model.query.filter(self.model.price >= min_price, self.model.price <= max_price).all()

    def get_places_with_amenity(self, amenity_id):
        """Retrieve places that have a specific amenity."""
        return self.model.query.filter(self.model.amenities.any(id=amenity_id)).all()

    def add_amenity_to_place(self, place_id, amenity):
        """Add an amenity to a place."""
        place = self.get(place_id)
        if not place:
            raise ValueError("Place not found")

        if amenity not in place.amenities:
            place.amenities.append(amenity)
            self.save(place)

    def remove_amenity_from_place(self, place_id, amenity):
        """Remove an amenity from a place."""
        place = self.get(place_id)
        if not place:
            raise ValueError("Place not found")

        if amenity in place.amenities:
            place.amenities.remove(amenity)
            self.save(place)
