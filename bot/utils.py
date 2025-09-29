import re

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class RegistrationForm(StatesGroup):
    get_phone = State()
    confirm = State()

class ChatState(StatesGroup):
    main_menu = State()
    student_info = State()
    about_us = State()



def normalize_phone(phone: str) -> str:
    # remove spaces, dashes, parentheses
    phone = re.sub(r"[^\d+]", "", phone)
    # if starts with +, remove it
    if phone.startswith("+"):
        phone = phone[1:]
    return phone