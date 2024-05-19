from zoneinfo import ZoneInfo
from aiogram import types, Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from config import mongodb_client
from aiogram.utils.keyboard import InlineKeyboardBuilder



main_router = Router()
db = mongodb_client.mat_db  # Название вашей базы данных
users_collection = db.users




@main_router.message(F.photo)
async def get_photo_id(message: Message):
    await message.reply(text=f"{message.photo[-1].file_id}")

@main_router.message(F.animation)
async def echo_gif(message: Message):
    file_id = message.animation.file_id
    print(file_id)
    await message.answer(text = file_id)



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
            ZoneInfo("Asia/Krasnoyarsk")).strftime("%Y-%m-%d %H:%M:%S")})
        await users_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"balance": self.balance}, "$push": {"history": {"amount": amount, "date": datetime.now().astimezone(
                ZoneInfo("Asia/Krasnoyarsk")).strftime("%Y-%m-%d %H:%M:%S")}}},
            upsert=True
        )
    
    async def save_to_db(self):
        await users_collection.update_one(
            {"user_id": self.user_id},
            {"$set": {"name": self.name, "balance": self.balance, "history": self.history}},
            upsert=True
        )

tanya = User(user_id=374056328, name="Таня")
masha = User(user_id=402748716, name="Маша")
vlad = User(user_id=964635576, name="Влад")

async def initialize_users():
   # await tanya.save_to_db()
    await tanya.load_from_db(users_collection)
    await masha.load_from_db(users_collection)
    await vlad.load_from_db(users_collection)






@main_router.message(Command('add_user'))
async def handle_payment(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    new_user = User(user_id=user_id, name=name)
    
    # Присваиваем переменной имя пользователя
    globals()[name] = new_user
    
    # Для проверки можно вывести информацию о новом пользователе
    print(f'Пользователь {name} создан с user_id: {user_id}')
    await new_user.save_to_db()

    await message.answer(f'Пользователь {name} создан с user_id: {user_id}')



@main_router.message(Command('statistic'))
async def get_statistic(message: Message):
    
    



    tanya_data = await users_collection.find_one({"user_id": 374056328})
    masha_data = await users_collection.find_one({"user_id": 402748716})

    if not tanya_data or not masha_data:
        await message.answer("Не удалось найти информацию о пользователях.")
        return

    # Получаем баланс обоих пользователей
    tanya_balance = tanya_data.get("balance", 0)
    masha_balance = masha_data.get("balance", 0)

    # Получаем историю начислений обоих пользователей
    tanya_history = tanya_data.get("history", [])
    masha_history = masha_data.get("history", [])

    # Формируем сообщение с балансом и историей начислений
    response_message = (
        f"Баланс пользователей:\n"
        f"Таня (ID: 374056328): {tanya_balance} руб.\n"
        f"Маша (ID: 402748716): {masha_balance} руб.\n\n"
        f"История начислений Тани:\n"
    )
    for record in tanya_history:
        response_message += f"- {record['date']}: {record['amount']} руб.\n"

    response_message += "\nИстория начислений Маши:\n"
    for record in masha_history:
        response_message += f"- {record['date']}: {record['amount']} руб.\n"
    
    # Отправляем сообщение
    await message.answer(response_message)


@main_router.message(Command('report'))
async def handle_payment(message: Message):
    builder = InlineKeyboardBuilder()
    
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"Маша сматерилась", callback_data='Masha_mat')],
                    [InlineKeyboardButton(
                        text=f"Таня сматерилась", callback_data='Tanya_mat')]
                ])
    builder.attach(InlineKeyboardBuilder.from_markup(markup))
    #await message.answer(text = 'На кого будем жаловаться?', reply_markup=markup)
    await message.answer_animation(animation='CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA', caption='На кого будем жаловаться?', reply_markup=markup, parse_mode="HTML" )





@main_router.callback_query(F.data.contains("Masha_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
  
    db = mongodb_client.mat_db  # Название вашей базы данных
    users_collection = db.users
    amount = 10
    await masha.update_balance(amount, users_collection)
    masha_data = await users_collection.find_one({"user_id": 402748716})
    balance = masha_data.get('balance', 'Неизвестно')

    # Формирование сообщения
    masha_message = f"<b>Мат зафиксирован!</b> \nШтрафы Маши: {balance} р."
    
    
    Balance: {masha_data['balance']}
    print(f'mashadata: {masha_data}')
    await query.message.edit_caption(animation = 'CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA', caption=masha_message, parse_mode='HTML')




    
@main_router.callback_query(F.data.contains("Tanya_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
 
    db = mongodb_client.mat_db  # Название вашей базы данных
    users_collection = db.users
    amount = 10
    await tanya.update_balance(amount, users_collection)
    tanya_data = await users_collection.find_one({"user_id": 374056328})
    balance = tanya_data.get('balance', 'Неизвестно')

    # Формирование сообщения
    tanya_message = f"<b>Мат зафиксирован!</b> \nШтрафы Тани: {balance} р."
    
    
    Balance: {tanya_data['balance']}
    print(f'mashadata: {tanya_data}')
    await query.message.edit_caption(animation = 'CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA', caption=tanya_message, parse_mode='HTML')