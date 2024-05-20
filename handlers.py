from zoneinfo import ZoneInfo
from aiogram import types, Router, F
from icecream import ic
from aiogram.filters import Command
from fsm_users import Form
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from additional_functions import get_recent_history_until_negative
from class_user import User
from config import mongodb_client
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import re

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
async def handle_new_user(message: Message, state: FSMContext):
    await message.answer(text='Введите cвоё имя')
    await state.set_state(Form.waiting_for_name)


@main_router.message(StateFilter(Form.waiting_for_name))
async def waiting_for_username(message: Message, state: FSMContext):
   # if type(message.text) is str and not message.text.isdigit():
    number_pattern = "\d"
    if not re.match(number_pattern, message.text):
        
        name = message.text
        user_id = message.from_user.id
        new_user = User(user_id=user_id, name=name)
        await message.answer(f'Пользователь {name} создан с user_id: {user_id}')
        await new_user.save_to_db(users_collection)
        await state.clear()
    else:
        await message.answer(f'введите корректное значение')


    
    

    


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

    await message.answer_photo(photo='AgACAgIAAxkBAAIBF2ZK_wFoWLYRnPoPcEFNpvLaVgURAAJT1zEb5tpZStW_sUqXiSnMAQADAgADeAADNQQ',
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
