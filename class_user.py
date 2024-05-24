from datetime import datetime
from zoneinfo import ZoneInfo
from config import mongodb_client
from icecream import ic

from mongo_connection import get_users_info

db = mongodb_client.mat_db
users_collection = db.users


class User:
    def __init__(self, user_id, name, balance=0, history=None):
        self.user_id = user_id
        self.name = name
        self.balance = balance
        self.history = history if history else []

    async def load_from_db(self, users_collection):
        user_data = await users_collection.find_one({"user_id": self.user_id})
        if user_data:
            self.balance = user_data.get('balance', 0)
            self.history = user_data.get('history', [])

    

    async def save_to_db(self, users_collection):
        await users_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"name": self.name, "balance": self.balance, "history": self.history}},
            upsert=True
        )

    async def reset_balance(self, users_collection):
        current_balance = self.balance
        self.balance = 0
        # Добавляем запись в историю с отрицательным значением текущего баланса
        self.history.append({
            "amount": -current_balance,
            "date": datetime.now().astimezone(ZoneInfo("Asia/Krasnoyarsk")).strftime("%Y-%m-%d %H:%M:%S")
        })
        # Сохраняем изменения в базу данных
        await users_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"balance": self.balance}, "$push": {"history": {"amount": -current_balance, "date": datetime.now().astimezone(
                ZoneInfo("Asia/Krasnoyarsk")).strftime("%d.%m.%Y %H:%M")}}},
            upsert=True
        )


async def get_current_balance(tg_id=None):
        user_data = await users_collection.find_one({"user_id": tg_id})
        ic(user_data)
        current_balance = user_data['balance']
        return current_balance



async def update_balance(amount, tg_id, balance):
        current_balance = await get_current_balance(tg_id)
        
        ic(current_balance)
        
        await users_collection.update_one(
            {"user_id": tg_id},
            {"$set": {"balance": current_balance+amount}, "$push": {"history": {"amount": amount, "date": datetime.now().astimezone(
                ZoneInfo("Asia/Krasnoyarsk")).strftime("%d.%m.%Y %H:%M")}}},
            upsert=True
        )