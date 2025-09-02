from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from decouple import config
from typing import Optional

from database.models import User
from schemas.user_schemas import UserCreate, UserLogin

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Şifreyi doğrula"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Şifreyi hashle"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Access token oluştur"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, db: Session) -> Optional[User]:
        """Token'ı doğrula ve kullanıcıyı getir"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                return None
            
            user = db.query(User).filter(User.email == email).first()
            return user
            
        except JWTError:
            return None
    
    def create_user(self, user_data: UserCreate, db: Session) -> User:
        """Yeni kullanıcı oluştur"""
        # Email kontrolü
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValueError("Email already registered")
        
        # Şifreyi hashle
        hashed_password = self.get_password_hash(user_data.password)
        
        # Kullanıcı oluştur
        db_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, user_data: UserLogin, db: Session) -> str:
        """Kullanıcı girişi yap ve token döndür"""
        user = db.query(User).filter(User.email == user_data.email).first()
        
        if not user or not self.verify_password(user_data.password, user.hashed_password):
            raise ValueError("Incorrect email or password")
        
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Token oluştur
        access_token_expires = timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return access_token
    
    def update_user_profile(self, user_id: int, profile_data: dict, db: Session) -> User:
        """Kullanıcı profil bilgilerini güncelle"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Güncellenebilir alanları kontrol et
        allowed_fields = ['full_name']
        
        for field, value in profile_data.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
