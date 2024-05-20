from datetime import datetime
from zoneinfo import ZoneInfo


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

    async def update_balance(self, amount, users_collection):
        self.balance += amount
        self.history.append({"amount": amount, "date": datetime.now().astimezone(
            ZoneInfo("Asia/Krasnoyarsk")).strftime("%d.%m.%Y %H:%M")})
        await users_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"balance": self.balance}, "$push": {"history": {"amount": amount, "date": datetime.now().astimezone(
                ZoneInfo("Asia/Krasnoyarsk")).strftime("%d.%m.%Y %H:%M")}}},
            upsert=True
        )

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