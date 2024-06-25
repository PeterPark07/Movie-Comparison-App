from pymongo import MongoClient
import os

# Connect to MongoDB
mongo_client = MongoClient(os.getenv('mongodb'))
database = mongo_client['Movie']
collection = os.getenv('movie_info')
movie_info = database[collection]
