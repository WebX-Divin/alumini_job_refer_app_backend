from fastapi import FastAPI, Request
import bcrypt
from schemas.model import SignupRequest
from db import users_collection

# FastAPI app instance
app = FastAPI()

# Route for handling signup
@app.post("/signup")
async def signup(request: Request, data: SignupRequest):
    # Extract data from the request body
    name = data.name
    email = data.email
    password = data.password
    confirm_password = data.confirmPassword
    mobile = data.mobile

    # Check if the passwords match
    if password != confirm_password:
        return {"error": "Passwords do not match"}

    # Check if the email already exists in the database
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return {"error": "Email already registered"}

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Create a new user in the database
    user = {
        "name": name,
        "email": email,
        "password": hashed_password.decode("utf-8"),
        "mobile": mobile,
    }
    users_collection.insert_one(user)

    return {"message": "User registered successfully"}