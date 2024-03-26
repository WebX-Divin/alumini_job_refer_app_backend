import time
from typing import Dict
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from db import users_collection

# JWT secret key
SECRET_KEY = "309dfa6215fcc621251e76cc4bc388474c03851d37959a1da07344f05047b6e9"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30000000

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTPBearer for token authentication
bearer_scheme = HTTPBearer()

# JWT functions
def create_access_token(data: Dict):
    to_encode = data.copy()
    expires = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"expires": expires})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except JWTError:
        return {}

def get_current_user(token: HTTPAuthorizationCredentials = Security(bearer_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decodeJWT(token.credentials)
        email = payload.get("email")

        if email is None:
            raise credentials_exception
        user = users_collection.find_one({"email": email}) 

        if user is None:
            raise credentials_exception
        
        # Convert ObjectId to string for serialization
        user['_id'] = str(user['_id'])

        return user
    except JWTError:
        raise credentials_exception
