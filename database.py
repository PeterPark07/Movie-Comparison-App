from pymongo import MongoClient
import os

# Connect to MongoDB
mongo_client = MongoClient(os.getenv('mongodb'))
database = mongo_client['Movie']
movie_info = database['movie_info']
