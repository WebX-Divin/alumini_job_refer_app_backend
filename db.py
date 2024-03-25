from pymongo import MongoClient

# MongoDB connection
MONGO_URI = "mongodb+srv://webx-divin:pass@alumini-job-refer-app.uj5baq2.mongodb.net/alumni_job_refer_app"
client = MongoClient(MONGO_URI)
db = client["alumni_job_refer_app"]
users_collection = db["users"]

