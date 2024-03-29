

import bcrypt
from auth import create_access_token, get_current_user, verify_password
from schemas.model import LoginRequest, PostRequest, SignupRequest
from db import users_collection, posts_collection
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


# Route for creating a new post
@app.post("/create_post")
async def create_post(request: Request, data: PostRequest):
    # Extract data from the request body
    job_role = data.job_role
    company_name = data.company_name
    job_description = data.job_description
    location = data.location
    is_part_time = data.is_part_time
    is_office = data.is_office
    salary = data.salary
    referral_code = data.referral_code
    apply_link = data.apply_link

    # Create a new post document
    post = {
        "job_role": job_role,
        "company_name": company_name,
        "job_description": job_description,
        "location": location,
        "is_part_time": is_part_time,
        "is_office": is_office,
        "salary": salary,
        "referral_code": referral_code,
        "apply_link": apply_link
    }

    # Save the post data to the database
    result = posts_collection.insert_one(post)

    return {
        "message": "Post created successfully",
        "post_id": str(result.inserted_id)
    }

# Route to list all posts
@app.get("/list_posts")
async def list_posts(current_user: dict = Depends(get_current_user)):

     # Verify if the user is authenticated
    if not current_user:
        return {"error": "Unauthorized"}

    # Retrieve all posts from the database
    posts = posts_collection.find()

    # Convert the posts to a list of dictionaries
    posts_list = []
    for post in posts:
        post_dict = {
            "id": str(post["_id"]),
            "job_role": post["job_role"],
            "company_name": post["company_name"],
            "job_description": post["job_description"],
            "location": post["location"],
            "is_part_time": post["is_part_time"],
            "is_office": post["is_office"],
            "salary": post["salary"],
            "referral_code": post["referral_code"],
            "apply_link": post["apply_link"]
        }
        posts_list.append(post_dict)

    return posts_list