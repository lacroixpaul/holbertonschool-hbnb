from app.persistence.repository import SQLAlchemyRepository
from app.models.user import User
from sqlalchemy.exc import IntegrityError

class UserRepository(SQLAlchemyRepository):
    """Repository specifically for handling user-related database operations."""

    def __init__(self):
        super().__init__(User)

    def get_user_by_email(self, email):
        """Retrieve a user by email."""
        return self.get_by_attribute('email', email)

    def create_user(self, user_data):
        """Create a new user, ensuring the email is unique."""
        try:
            user = User(**user_data)
            user.hash_password(user_data['password'])
            self.add(user)
            return user
        except IntegrityError:
            raise ValueError("Email already exists!")

    def update_user(self, user_id, user_data):
        """Update a user without modifying the password unless provided."""
        user = self.get(user_id)
        if not user:
            raise ValueError("User not found!")

        if "password" in user_data:
            user.hash_password(user_data["password"])
            del user_data["password"]

        self.update(user_id, user_data)
        return user

    def delete_user(self, user_id):
        """Delete a user from the database."""
        user = self.get(user_id)
        if not user:
            raise ValueError("User not found!")
        self.delete(user_id)
