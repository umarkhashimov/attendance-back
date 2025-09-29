
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class RegistrationForm(StatesGroup):
    get_phone = State()
    confirm = State()

class ChatState(StatesGroup):
    main_menu = State()
    student_info = State()
    about_us = State()
