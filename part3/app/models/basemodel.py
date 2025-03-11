from app import db
import uuid
from datetime import datetime
from sqlalchemy.sql import func

class BaseModel(db.Model):

    __abstract__ = True 

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())


    def save(self):
        """Update the updated_at timestamp and commit changes to the database"""
        self.updated_at = func.now()
        db.session.add(self)
        db.session.commit()

    def update(self, data):
        """Update the attributes of the object based on the provided dictionary"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        
    def is_max_length(self, name, value, max_length):
        """Check if a string value exceeds a maximum length"""
        if len(value) > max_length:
            raise ValueError(f"{name} must be {max_length} characters max.")

    def is_between(self, name, value, min_val, max_val):
        """Check if a numeric value is within a specified range"""
        if not min_val <= value <= max_val:
            raise ValueError(f"{name} must be between {min_val} and {max_val}.")
