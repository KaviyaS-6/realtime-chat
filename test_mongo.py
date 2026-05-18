from pymongo import MongoClient
import os

# Get MongoDB Atlas URL from environment variable
MONGO_URL = os.getenv("MONGO_URL")

# Connect to MongoDB Atlas
client = MongoClient(MONGO_URL)

# Database
db = client["chat_app"]

# Collection
collection = db["messages"]

# Test data
data = {
    "user": "Kaviya",
    "message": "Hello MongoDB Atlas"
}

# Insert data
collection.insert_one(data)

print("Data inserted successfully 🚀")