from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

from database import SessionLocal
from models import User

# ==========================
# CONFIG
# ==========================

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Use Argon2 instead of bcrypt to avoid 72-character limit
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# ==========================
# PASSWORD UTILS
# ==========================

def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against the hashed password."""
    return pwd_context.verify(plain, hashed)

# ==========================
# TOKEN UTILS
# ==========================

def create_access_token(username: str, role: str):
    """Create a JWT access token."""
    payload = {
        "sub": username,
        "role": role,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(username: str):
    """Create a JWT refresh token."""
    payload = {
        "sub": username,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# DEFAULT ADMIN CREATION
# ==========================

# Default admin creation should use 'hashed_password'
def create_default_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print("✅ Default admin created (username=admin, password=admin123)")
    finally:
        db.close()

