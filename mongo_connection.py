    
from config import mongodb_client

db = mongodb_client.mat_db
users_collection = db.users

async def get_names(names):

    for i in users_collection.find():
        usernames = []
        usernames.append(names)
