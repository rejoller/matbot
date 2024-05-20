from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup



class Form(StatesGroup):
    waiting_for_name = State()
