from icecream import ic
from config import mongodb_client

db = mongodb_client.mat_db
users_collection = db.users




async def get_users_info():

    user_all_data = []
    async for document in db.users.find():

    
        if 'user_id' in document:
    
            for user_id, user_data in document.items():

                user_info ={
                    'tg_id':  document['user_id'],
                    'name': document['name'],
                    'balance': document['balance'],
                    'history': document['history']



                }
        
            user_all_data.append(user_info)
            
    return user_all_data