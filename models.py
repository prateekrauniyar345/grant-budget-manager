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
    duration = db.Column(Integer, nullable=False)
    start_date = db.Column(Date, nullable=False)  # Start date of the grant
    end_date = db.Column(Date, nullable=False)  # End date of the grant
    status = db.Column(Enum('Draft', 'Submitted', 'Approved', 'Rejected', 'Completed'), default='Draft')  # Grant status
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship with User
    user = db.relationship('User', backref=db.backref('grants', lazy=True))
    personnel = db.relationship('GrantPersonnel', backref='grants', cascade="all, delete-orphan")
    travels = db.relationship('GrantTravel', backref='grants', cascade="all, delete-orphan")
    materials = db.relationship('GrantMaterial', backref='grants', cascade="all, delete-orphan")


    def __repr__(self):
        return f'<Grant {self.title}>'



# Grant Personnel
class GrantPersonnel(db.Model):
    __tablename__ = 'grants_personnel'

    id = db.Column(Integer, primary_key=True)
    grant_id = db.Column(Integer, db.ForeignKey('grants.id'), nullable=False)
    name = db.Column(String(100), nullable=True, default=None)
    position = db.Column(String(100), nullable=True, default=None)
    year = db.Column(Integer, nullable=True, default=None)
    estimated_hours = db.Column(DECIMAL(10, 2), nullable=True, default=None)

    # grant = db.relationship('Grant', backref=db.backref('personnel', lazy=True))


# Grant Travel
class GrantTravel(db.Model):
    __tablename__ = 'grants_travel'

    id = db.Column(Integer, primary_key=True)
    grant_id = db.Column(Integer, db.ForeignKey('grants.id'), nullable=False)
    travel_type = db.Column(Enum('Domestic', 'International'), nullable=True, default=None)
    name = db.Column(String(255), nullable=True, default=None)
    description = db.Column(Text, nullable=True, default=None)
    year = db.Column(Integer, nullable=True, default=None)
    amount = db.Column(DECIMAL(10, 2), nullable=True, default=None)

    # grant = db.relationship('Grant', backref=db.backref('travels', lazy=True))


# Grant Materials & Supplies
class GrantMaterial(db.Model):
    __tablename__ = 'grants_materials'

    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.Integer, db.ForeignKey('grants.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_categories.id'), nullable=True, default=None)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('expense_subcategories.id'), nullable=True, default=None)
    cost = db.Column(db.DECIMAL(10, 2), nullable=True, default=None)
    description = db.Column(db.Text, nullable=True, default=None)
    year = db.Column(db.Integer, nullable=True, default=None)

    # Relationships
    # grant = db.relationship('Grant', backref=db.backref('materials', lazy=True))
    category = db.relationship('ExpenseCategory', backref=db.backref('materials', lazy=True))
    subcategory = db.relationship('ExpenseSubcategory', backref=db.backref('materials', lazy=True))

    def __repr__(self):
        return f"<GrantMaterial(grant_id={self.grant_id}, category_id={self.category_id}, subcategory_id={self.subcategory_id}, year={self.year})>"



# expsense category
class ExpenseCategory(db.Model):
    __tablename__ = 'expense_categories'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False, unique=True)  # Category name (e.g., "Travel")
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Relationship to subcategories
    subcategories = db.relationship('ExpenseSubcategory', backref='category', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<ExpenseCategory {self.name}>'

# expense subcategory
class ExpenseSubcategory(db.Model):
    __tablename__ = 'expense_subcategories'

    id = db.Column(Integer, primary_key=True)
    category_id = db.Column(Integer, db.ForeignKey('expense_categories.id'), nullable=False)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)

    # Optional reverse relationship already handled by `backref='category'` above

    def __repr__(self):
        return f'<ExpenseSubcategory {self.name} (Category ID: {self.category_id})>'










############################################
# Perosneels table
############################################
# PI Table
class PI(db.Model):
    __tablename__ = 'pi_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<PI Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# Co-PI Table
class CoPI(db.Model):
    __tablename__ = 'copi_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<CoPI Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# Professional Staff Table
class ProfessionalStaff(db.Model):
    __tablename__ = 'professionalstaff_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<ProfessionalStaff Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# Postdoc Table
class Postdoc(db.Model):
    __tablename__ = 'postdoc_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<Postdoc Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# GRA Table
class GRA(db.Model):
    __tablename__ = 'gra_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<GRA Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# Temp Help Table
class TempHelp(db.Model):
    __tablename__ = 'temphelp_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<TempHelp Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"

# Undergrad Table
class Undergrad(db.Model):
    __tablename__ = 'undergrad_table'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    position = db.Column(db.String(100), nullable=False)
    expected_hourly_salary = db.Column(db.DECIMAL(10, 2), nullable=False)

    def __repr__(self):
        return f"<Undergrad Name: {self.full_name}, Email: {self.email}, Position: {self.position}, Hourly Salary: ${self.expected_hourly_salary}>"
