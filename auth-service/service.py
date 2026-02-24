from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt

from models import UserCreate, UserInDB
from data_service import AuthMockDataService

# Secret key to sign JWT token
SECRET_KEY = "super-secret-gateway-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self):
        self.data_service = AuthMockDataService()

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def get_password_hash(self, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        user = self.data_service.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, user_in: UserCreate) -> Optional[UserInDB]:
        existing_user = self.data_service.get_user_by_username(user_in.username)
        if existing_user:
            return None # User already exists
        hashed_password = self.get_password_hash(user_in.password)
        new_user = self.data_service.add_user(username=user_in.username, hashed_password=hashed_password)
        return new_user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
