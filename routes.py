

import bcrypt
from auth import create_access_token, get_current_user, verify_password
from schemas.model import LoginRequest, SignupRequest
from db import users_collection
from fastapi import Depends, HTTPException, Request, FastAPI

# FastAPI app instance
app = FastAPI()

# Route for handling signup
@app.post("/signup")
async def signup(request: Request, data: SignupRequest):
    # Extract data from the request body
    name = data.name
    email = data.email
    password = data.password
    mobile = data.mobile

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

    # Generate and save JWT token
    token = create_access_token(data={"email": email})
    users_collection.update_one({"email": email}, {"$set": {"token": token}})

    return {
        "token": token,
        "message": "User registered successfully"
    }


# Route for handling login
@app.post("/login")
async def login(request: Request, data: LoginRequest):
    # Find the user in the database
    user = users_collection.find_one({"mobile": data.mobile})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # Verify the password
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    # Generate and return JWT token
    token = user.get("token")
    if not token:
        token = create_access_token(data={"email": user["email"]})
        users_collection.update_one({"mobile": data.mobile}, {"$set": {"token": token}})

    return {
        "token": token,
        "message": "User login successfully"
    }


@app.get("/users")
async def list_users(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
