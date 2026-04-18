"""
MongoDB-compatible password context only.
SQLAlchemy models removed - using dicts/schemas directly with Motor.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

