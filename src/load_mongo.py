from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

def get_database():
    # Connect to MongoDB
    client = MongoClient(os.getenv('MONGODB_URI'))
    return client['trace-kanji']

if __name__ == "__main__":
    dbname = get_database()
