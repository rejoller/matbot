from zoneinfo import ZoneInfo
from aiogram import types, Router, F
from icecream import ic
from aiogram.filters import Command

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from config import mongodb_client




main_router = Router()



db = mongodb_client.mat_db 
users_collection = db.users


@main_router.message(F.photo)
async def get_photo_id(message: Message):
    await message.reply(text=f"{message.photo[-1].file_id}")


@main_router.message(F.animation)
async def echo_gif(message: Message):
    file_id = message.animation.file_id
    print(file_id)
    await message.answer(text=file_id)


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



tanya = User(user_id=374056328, name="Таня")
masha = User(user_id=402748716, name="Маша")
vlad = User(user_id=964635576, name="Влад")


async def initialize_users():

    await tanya.load_from_db(users_collection)
    await masha.load_from_db(users_collection)
    await vlad.load_from_db(users_collection)


@main_router.message(Command('reset'))
async def handle_reset(message: Message):

    await masha.reset_balance(users_collection)
    await tanya.reset_balance(users_collection)
    await message.answer('сброшено')


@main_router.message(Command('add_user'))
async def handle_payment(message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    new_user = User(user_id=user_id, name=name)

    globals()[name] = new_user

    print(f'Пользователь {name} создан с user_id: {user_id}')
    await new_user.save_to_db()

    await message.answer(f'Пользователь {name} создан с user_id: {user_id}')







async def get_recent_history_until_negative(history):
    recent_history = []
    
    for record in reversed(history):
        recent_history.append(record)
        if record['amount'] < 0:
            break
    return recent_history

# Предполагаем, что вы находитесь внутри асинхронной функции или окружения





@main_router.message(Command('statistic'))
async def get_statistic(message: Message):

    tanya_data = await users_collection.find_one({"user_id": 374056328})
    
    masha_data = await users_collection.find_one({"user_id": 402748716})
   
    
    if not tanya_data or not masha_data:
        await message.answer("Не удалось найти информацию о пользователях.")
        return
    tanya_balance = tanya_data.get("balance", 0)
    masha_balance = masha_data.get("balance", 0)
    

    tanya_history = tanya_data.get("history", [])
    masha_history = masha_data.get("history", [])

    tanya_recent_history = await get_recent_history_until_negative(history=tanya_history)
    masha_recent_history = await get_recent_history_until_negative(history=masha_history)


    response_message = (
        f"<b>Статистика матюков</b>\n"
        f"Таня: {tanya_balance} руб.\n"
        f"Маша: {masha_balance} руб.\n\n"
        f"<b>История штрафов Тани:</b>\n"
    )
    for record in reversed(tanya_recent_history):
        response_message += f"{record['date']} - {record['amount']} руб.\n"

    response_message += "\n<b>История штрафов Маши:</b>\n"
    for record in reversed(masha_recent_history):
        response_message += f"{record['date']} - {record['amount']} руб.\n"


    await message.answer_photo(photo= 'AgACAgIAAxkBAAIBF2ZK_wFoWLYRnPoPcEFNpvLaVgURAAJT1zEb5tpZStW_sUqXiSnMAQADAgADeAADNQQ',
                               caption=response_message, parse_mode="HTML")


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

    await message.answer_animation(animation='CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA', 
                                   caption='На кого будем жаловаться?', reply_markup=markup, parse_mode="HTML")


@main_router.callback_query(F.data.contains("Masha_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
    amount = 10
    await masha.update_balance(amount, users_collection)
    masha_data = await users_collection.find_one({"user_id": 402748716})
    balance = masha_data.get('balance', 'Неизвестно')


    masha_message = f"<b>Мат зафиксирован!</b> \nШтрафы Маши: {balance} р."

    Balance: {masha_data['balance']}

    await query.message.edit_caption(animation='CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA', 
                                     caption=masha_message, parse_mode='HTML')


@main_router.callback_query(F.data.contains("Tanya_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
    amount = 10
    await tanya.update_balance(amount, users_collection)
    tanya_data = await users_collection.find_one({"user_id": 374056328})
    balance = tanya_data.get('balance', 'Неизвестно')
    tanya_message = f"<b>Мат зафиксирован!</b> \nШтрафы Тани: {balance} р."
    Balance: {tanya_data['balance']}

    await query.message.edit_caption(animation='CgACAgIAAxkBAANVZkcSILbeKabcnkR4YR4j2Jl8BuoAAoFEAAL0uzlKcwwmpVIVQWU1BA',
                                     caption=tanya_message, parse_mode='HTML')
