
from bson import ObjectId
import bcrypt
from auth import create_access_token, get_current_user, verify_password
from schemas.model import LoginRequest, PostRequest, PredictionInput, SignupRequest
from db import users_collection, posts_collection, predictions_collection
from fastapi import Depends, HTTPException, Request, FastAPI, Body, status
import pickle
import numpy as np

app = FastAPI()

@app.get('/')
def home():
    return {'message: Alumini Job Refer App with ML Skill Finder'}

@app.post("/signup")
async def signup(request: Request, data: SignupRequest):

    name = data.name
    email = data.email
    password = data.password
    mobile = data.mobile
    userType = data.userType

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
        "userType": userType
    }
    users_collection.insert_one(user)

    # Generate and save JWT token
    token = create_access_token(data={"email": email})
    users_collection.update_one({"email": email}, {"$set": {"token": token}})

    return {
        "token": token,
        "message": "User registered successfully"
    }


@app.post("/login")
async def login(request: Request, data: LoginRequest):
    
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



@app.post("/create_post")
async def create_post(request: Request, data: PostRequest, current_user: dict = Depends(get_current_user)):

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


# Load the pre-trained model
loaded_model = pickle.load(open("ml_model/careerlast.pkl", 'rb'))
@app.post("/predict")
def predict(input_data: PredictionInput = Body(...), current_user: dict = Depends(get_current_user)):
   
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
        "user_name": str(current_user["name"]),
        "input_data": input_data.model_dump(),
        "prediction": prediction[0]  # Store the prediction as a string
    }
    predictions_collection.insert_one(prediction_data)

    return {"prediction": prediction[0]}  # Return the prediction as a string

@app.get("/list_users")
async def list_users(current_user: dict = Depends(get_current_user)):
    # Check if the user is an admin (or any other role that has permission to view all users)
    if current_user.get("userType") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    # Retrieve all users from the database
    all_users = list(users_collection.find())

    # Convert ObjectId to string for serialization for each user
    for user in all_users:
        user['_id'] = str(user['_id'])

    return {"users": all_users}

@app.get("/list_posts")
async def list_posts(current_user: dict = Depends(get_current_user)):

    if current_user.get("userType") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

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

@app.get("/list_predictions")
def list_predictions(current_user: dict = Depends(get_current_user)):
   
    if current_user.get("userType") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

   # Retrieve all predictions from the database
    all_predictions = list(predictions_collection.find())

    # Prepare the predictions to be returned
    predictions = []
    for prediction in all_predictions:
        # Fetch user details including name
        user_details = predictions_collection.find_one({"user_name": prediction["user_name"]})
        if user_details:
            user_name = user_details["user_name"]  # Use "user_name" field
        else:
            user_name = "Unknown"
        
        predictions.append({
            "user_name": user_name,
            "prediction": prediction["prediction"]
        })

    return predictions


@app.delete("/delete_post")
async def delete_post(post_index: int, current_user: dict = Depends(get_current_user)):

    if current_user.get("userType") != "Admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    # Retrieve all posts from the database
    posts = posts_collection.find()

    # Convert the posts to a list of dictionaries
    posts_list = list(posts)

    # Check if the post index is within range
    if post_index < 0 or post_index >= len(posts_list):
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete the post from the list
    deleted_post = posts_list.pop(post_index)

    # Convert ObjectId to string for serialization
    deleted_post['_id'] = str(deleted_post['_id'])

    # Update the database by removing the corresponding document
    deleted_post_id = deleted_post['_id']
    deleted_post_id_obj = ObjectId(deleted_post_id)
    deleted_count = posts_collection.delete_one({"_id": deleted_post_id_obj})

    if deleted_count.deleted_count == 0:
        raise HTTPException(status_code=500, detail="Failed to delete post from the database")

    return {"message": "Post deleted successfully", "deleted_post": deleted_post}

