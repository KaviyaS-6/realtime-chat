from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["chat_app"]

collection = db["messages"]

data = {
    "user": "Kaviya",
    "message": "Hello MongoDB"
}

collection.insert_one(data)

print("Data inserted successfully")