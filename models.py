# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from dotenv import load_dotenv
# from datetime import datetime
# from flask_login import UserMixin

# import os


# # Load environment variables
# load_dotenv()



# db = SQLAlchemy()
# bcrypt = Bcrypt()


# # User Model
# class User(db.Model,UserMixin ):
#     __tablename__ = 'users'  # Specify the correct table name

#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     username = db.Column(db.String(50), nullable=False, unique=True)
#     email = db.Column(db.String(100), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)  # Store hashed password
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def set_password(self, password):
#         """Hash the password before saving it"""
#         self.password = bcrypt.generate_password_hash(password).decode('utf-8')

#     def check_password(self, password):
#         """Verify a password"""
#         return bcrypt.check_password_hash(self.password, password)
    
#     def __repr__(self):
#         return f'<User {self.username}>'





from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Integer, String, Date, Text, DECIMAL, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base

import os

# Load environment variables
load_dotenv()

# Initialize the database and bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()

# Base for model inheritance
Base = declarative_base()

# User Model
class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Specify the correct table name

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
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
    
    def __repr__(self):
        return f'<User {self.username}>'



# Grant Model
class Grant(db.Model):
    __tablename__ = 'grants'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key linking to users table
    title = db.Column(String(255), nullable=False)  # Grant title
    description = db.Column(Text)  # Detailed description of the grant
    funding_agency = db.Column(String(255), nullable=False)  # Name of the funding agency (e.g., NSF, NIH)
    total_funding = db.Column(DECIMAL(15, 2), nullable=False)  # Total funding amount
    start_date = db.Column(Date, nullable=False)  # Start date of the grant
    end_date = db.Column(Date, nullable=False)  # End date of the grant
    status = db.Column(Enum('Draft', 'Submitted', 'Approved', 'Rejected', 'Completed'), default='Draft')  # Grant status
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship with User
    user = db.relationship('User', backref=db.backref('grants', lazy=True))

    def __repr__(self):
        return f'<Grant {self.title}>'
