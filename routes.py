

import bcrypt
from auth import create_access_token, get_current_user, verify_password
from schemas.model import LoginRequest, PostRequest, PredictionInput, SignupRequest
from db import users_collection, posts_collection, predictions_collection
from fastapi import Depends, HTTPException, Request, FastAPI, Body
import pickle
import numpy as np

# FastAPI app instance
app = FastAPI()

@app.get('/')
def home():
    return {'message: Alumini Job Refer App - AI Assisted API'}

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


@app.get("/list_users")
async def list_users(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}


# Route for creating a new post
@app.post("/create_post")
async def create_post(request: Request, data: PostRequest, current_user: dict = Depends(get_current_user)):

     # Verify if the user is authenticated
    if not current_user:
        return {"error": "Unauthorized"}

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

# Load the pre-trained model
loaded_model = pickle.load(open("ml_model/careerlast.pkl", 'rb'))

@app.post("/predict")
def predict(input_data: PredictionInput = Body(...), current_user: dict = Depends(get_current_user)):
    # Verify if the user is authenticated
    if not current_user:
        return {"error": "Unauthorized"}

    # Convert input data to a NumPy array
    input_array = np.array([
        input_data.Database_Fundamentals,
        input_data.Computer_Architecture,
        input_data.Distributed_Computing_Systems,
        input_data.Cyber_Security,
        input_data.Networking,
        input_data.Development,
        input_data.Programming_Skills,
        input_data.Project_Management,
        input_data.Computer_Forensics_Fundamentals,
        input_data.Technical_Communication,
        input_data.AI_ML,
        input_data.Software_Engineering,
        input_data.Business_Analysis,
        input_data.Communication_skills,
        input_data.Data_Science,
        input_data.Troubleshooting_skills,
        input_data.Graphics_Designing
    ], dtype=np.float64)

    # Reshape the input array to match the expected input shape of the model
    input_array = input_array.reshape(1, -1)

    # Make predictions using the loaded model
    prediction = loaded_model.predict(input_array)

    # Save the prediction to the database
    prediction_data = {
        "user_id": str(current_user["_id"]),
        "input_data": input_data.model_dump(),
        "prediction": prediction[0]  # Store the prediction as a string
    }
    predictions_collection.insert_one(prediction_data)

    return {"prediction": prediction[0]}  # Return the prediction as a string


@app.get("/list_predictions")
def get_predictions(current_user: dict = Depends(get_current_user)):
    # Verify if the user is authenticated
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Retrieve predictions for the current user from the database
    user_predictions = predictions_collection.find({"user_id": str(current_user["_id"])})

    # Convert the cursor to a list and get its length to count the documents
    predictions_count = len(list(user_predictions))

    # Reset the cursor to the beginning to iterate over it again
    user_predictions.rewind()

    # If there are no predictions found, return an empty list
    if predictions_count == 0:
        return []

    # Prepare the predictions to be returned
    predictions = []
    for prediction in user_predictions:
        predictions.append({
            "input_data": prediction["input_data"],
            "prediction": prediction["prediction"]
        })

    return predictions
