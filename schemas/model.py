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
    userType: str

class LoginRequest(BaseModel):
    mobile: str
    password: str

class PostRequest(BaseModel):
    job_role: str
    company_name: str
    job_description: str
    location: str
    is_part_time: bool
    is_office: bool
    salary: int
    referral_code: str
    apply_link: str

class PredictionInput(BaseModel):
    Database_Fundamentals: int
    Computer_Architecture: int
    Distributed_Computing_Systems: int
    Cyber_Security: int
    Networking: int
    Development: int
    Programming_Skills: int
    Project_Management: int
    Computer_Forensics_Fundamentals: int
    Technical_Communication: int
    AI_ML: int
    Software_Engineering: int
    Business_Analysis: int
    Communication_skills: int
    Data_Science: int
    Troubleshooting_skills: int
    Graphics_Designing: int

class UserDetails(BaseModel):
    token: str