from pydantic import BaseModel, EmailStr, Field

# Pydantic model for request body
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirmPassword: str
    mobile: str