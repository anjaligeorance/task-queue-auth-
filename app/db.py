from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["task_db"]
tasks_collection = db["tasks"]

def insert_task(task):
    tasks_collection.insert_one(task)
