from zoneinfo import ZoneInfo
from aiogram import types, Router, F
from icecream import ic
from aiogram.filters import Command
from fsm_users import Form
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from datetime import datetime
from additional_functions import get_recent_history_until_negative
from class_user import User, update_balance
from config import mongodb_client
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import re
from content import report_animation, statistic_photo
from mongo_connection import get_users_info
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
    print('в ресет ')
    await masha.reset_balance(users_collection)
    await tanya.reset_balance(users_collection)
    await message.answer('сброшено')

@main_router.message(Command('statistic'))
async def get_statistic(message: Message):
    print('в статистике')
    recent_histories = []
    user_all_data = []
    response = await get_users_info()
    response_text = ''
    #recent_histories = await get_recent_history_until_negative(response[0]['history'])
   # ic(recent_histories)
    for i, response in enumerate(response, 0):
            
        
            response_text += f"ID {response['tg_id']}\n"
            response_text += f"имя {response['name']}\n"
            response_text += f"баланс {response['balance']}\n"
            response_text += f"история {await get_recent_history_until_negative(response['history'])}\n"
            

    await message.answer(response_text)


@main_router.message(Command('add_user'))
async def handle_new_user(message: Message, state: FSMContext):
    print('в адд юзер')
    await message.answer(text='Введите cвоё имя')
    await state.set_state(Form.waiting_for_name)




@main_router.message(StateFilter(Form.waiting_for_name))
async def waiting_for_username(message: Message, state: FSMContext):
    print('в waiting_for_username')
    number_pattern = "[а-яА-Я]+"
    if re.fullmatch(number_pattern, message.text):

        name = message.text
        user_id = message.from_user.id
        new_user = User(user_id=user_id, name=name)

        if await users_collection.find_one({"name": name}):
            await message.answer(f'Имя {name} занято, выберите другое')
        else:
            await message.answer(f'Пользователь {name} создан!')
            await new_user.save_to_db(users_collection)
            await state.clear()
    else:
        await message.answer(f'введите корректное значение')




@main_router.message(Command('report'))
async def handle_payment(message: Message, state: FSMContext):

    builder = InlineKeyboardBuilder()
    bad_users = await get_users_info()
    for i, bad_users in  enumerate(bad_users, 0):
        name = bad_users['name']
        tg_id = bad_users['tg_id']
        balance = bad_users['balance']


        
        
        builder.button(text=f'Пользователь {name} сматерился', callback_data=f'{tg_id}_mat')
            

        builder.adjust(1)
        keyboard = builder.as_markup()
        
    await message.answer_animation(animation=report_animation,
                                   caption='На кого будем жаловаться?', reply_markup=keyboard, parse_mode="HTML")

'''
@main_router.callback_query(F.data.contains("Masha_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
    print('в Маша мат')
    amount = 10
    await masha.update_balance(amount, users_collection)
    masha_data = await users_collection.find_one({"user_id": 402748716})
    balance = masha_data.get('balance', 'Неизвестно')

    masha_message = f"<b>Мат зафиксирован!</b> \nШтрафы Маши: {balance} р."

    Balance: {masha_data['balance']}

    await query.message.edit_caption(animation=report_animation,
                                     caption=masha_message, parse_mode='HTML')

'''

@main_router.callback_query(F.data.contains(f"_mat"))
async def handle_masha_mat(query: types.CallbackQuery):
    print('в Маша мат')
    tg_id = int(query.data.split('_')[0])
    
    
    amount = 10
    await update_balance(amount, tg_id, balance)
    user_data = await users_collection.find_one({"user_id": tg_id})
    balance = user_data.get('balance', 'Неизвестно')

    masha_message = f"<b>Мат зафиксирован!</b> \nШтрафы {balance} р."

   
    await query.message.edit_caption(animation=report_animation,
                                     caption=masha_message, parse_mode='HTML')

