"""
Authentication service - JWT token handling
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Handles authentication and JWT tokens"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token
        
        Args:
            data: Payload to encode (e.g., {"sub": username, "user_id": 123})
            expires_delta: Token expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate JWT token
        
        Returns:
            Decoded payload or None if invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


# Simple in-memory user store (replace with database in production)
class UserStore:
    """Simple in-memory user storage"""
    
    def __init__(self):
        self.users = {}
        self.next_id = 1
        
        # Add demo user
        self._add_demo_user()
    
    def _add_demo_user(self):
        """Add a demo user for testing"""
        self.users["demo"] = {
            "user_id": 1,
            "username": "demo",
            "email": "demo@reelsense.com",
            "hashed_password": AuthService.get_password_hash("demo123"),
            "created_at": datetime.utcnow()
        }
        self.next_id = 2
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        return self.users.get(username)
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create a new user"""
        if username in self.users:
            raise ValueError("Username already exists")
        
        user = {
            "user_id": self.next_id,
            "username": username,
            "email": email,
            "hashed_password": AuthService.get_password_hash(password),
            "created_at": datetime.utcnow()
        }
        
        self.users[username] = user
        self.next_id += 1
        
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        
        return user


# Global user store instance
user_store = UserStore()
