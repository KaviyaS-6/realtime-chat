from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")

client = MongoClient(MONGO_URL)

db = client["chat_db"]
messages_collection = db["messages"]

print("MongoDB Connected 🚀")