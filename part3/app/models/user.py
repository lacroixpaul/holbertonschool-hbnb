from app import db, bcrypt
from .basemodel import BaseModel
import re
from sqlalchemy.orm import validates


class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    @validates('email')
    def validate_email(self, key, email):
        """Validate the email format before storing it."""
        if not isinstance(email, str):
            raise TypeError("Email must be a string")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email format")
        return email

    @validates('first_name', 'last_name')
    def validate_name(self, key, value):
        """Validate the first name and last name length before storing."""
        if not isinstance(value, str):
            raise TypeError(f"{key.replace('_', ' ').title()} must be a string")
        if len(value) > 50:
            raise ValueError(f"{key.replace('_', ' ').title()} must be at most 50 characters")
        return value

    def to_dict(self):
        """Convert the User object to a dictionary."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'is_admin': self.is_admin
        }
