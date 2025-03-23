from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime

import os


# Load environment variables
load_dotenv()



db = SQLAlchemy()
bcrypt = Bcrypt()


# User Model
class User(db.Model):
    __tablename__ = 'users'  # Specify the correct table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)  # Store hashed password
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hash the password before saving it"""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify a password"""
        return bcrypt.check_password_hash(self.password, password)




