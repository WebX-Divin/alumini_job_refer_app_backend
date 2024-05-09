from pymongo import MongoClient

# MongoDB connection
MONGO_URI = ""
client = MongoClient(MONGO_URI)
db = client["alumni_job_refer_app"]
users_collection = db["users"]
posts_collection = db["posts"]
predictions_collection = db["predictions"]

