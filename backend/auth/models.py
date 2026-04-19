"""
MongoDB-compatible password context only.
SQLAlchemy models removed - using dicts/schemas directly with Motor.
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

