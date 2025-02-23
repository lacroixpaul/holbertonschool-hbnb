#!/usr/bin/python3
"""
Module user

This module defines the 'User' class, which represents a system user.
It inherits from BaseModel (defined in basemodel.py).

The `User` class includes the following attributes:
- first_name (str): The first name of the user (required, maximum length of 50 characters).
- last_name (str): The last name of the user (required, maximum length of 50 characters).
- email (str): The email address of the user (required, must follow standard email format validation).
- is_admin (bool): Indicates whether the user has administrative privileges (default: False).
- places (list): A list of places owned by the user.
- ID: Inherited from BaseModel.
- Date of creation / update: Inherited from BaseModel.

Example usage:
    user = User(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        is_admin=False
    )
"""
import re
from .basemodel import BaseModel


class User(BaseModel):
    """Represents a user with validation for name and email."""

    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()  # Initialize BaseModel (UUID, created_at, updated_at)
        self.first_name = self.validate_name(first_name)
        self.last_name = self.validate_name(last_name)
        self._email = self.validate_email(email)
        self._is_admin = is_admin
        self.places = []

    def validate_name(self, name):
        """Validates that the name is a string with a maximum length of 50."""
        if not isinstance(name, str) or len(name) > 50:
            raise ValueError("Maximum length of 50 characters")
        return name

    @staticmethod
    def validate_email(email):
        """Validates if the email follows a standard format."""
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

        if not re.match(pattern, email):
            raise ValueError("The email address is not valid.")

        return email

    @property
    def email(self):
        """Getter for email."""
        return self._email

    @email.setter
    def email(self, value):
        """Setter for email with validation."""
        self._email = self.validate_email(value)

    @property
    def is_admin(self):
        """Getter for is_admin."""
        return self._is_admin

    @is_admin.setter
    def is_admin(self, value):
        """Setter for is_admin."""
        if not isinstance(value, bool):
            raise ValueError("is_admin must be a boolean")
        self._is_admin = value

    def to_dict(self):
        """Converts the user instance to a dictionary."""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
