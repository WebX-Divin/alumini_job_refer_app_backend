from pydantic import BaseModel, EmailStr
from typing import Union

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None

# Pydantic model for request body
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    mobile: str

class LoginRequest(BaseModel):
    mobile: str
    password: str