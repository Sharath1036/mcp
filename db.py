from pymongo import MongoClient
import os

def get_mongo_client():
    # You can set MONGODB_URI as an environment variable for production
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    return MongoClient(uri)

def get_employees_collection():
    client = get_mongo_client()
    db = client["mcp"]
    return db["employee"] 