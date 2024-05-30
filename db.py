from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["traffic_estimation"]
users_collection = db["users"]
speeding_cars_db = db["speeding_cars"]
user_images_db = db["user_detections"]
pde_admin_db = db["pde_detections"]
traffic_analysis_db = db["traffic_analysis"]


# Function to hash passwords
def hash_password(password):
    return pbkdf2_sha256.hash(password)


# Function to verify passwords
def verify_password(password, hashed_password):
    return pbkdf2_sha256.verify(password, hashed_password)
