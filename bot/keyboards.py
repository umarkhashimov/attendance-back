from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder
from .database import get_user

async def get_main_menu_keyboard(uid):
    user = await get_user(uid)

    keys = [
        [
            KeyboardButton(text='🔑 Войти') if not user else KeyboardButton(text='🗂️ Данные Ученика'),
            KeyboardButton(text='📖 Материалы'),
        ],
        [
            KeyboardButton(text='🧑‍🏫 Учителя'),
            KeyboardButton(text='🏫 О центре'),
        ]

    ]

    kb = ReplyKeyboardMarkup(keyboard=keys, resize_keyboard=True, selective=True)

    return kb

request_phone_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="📱 Отправить мой контакт", request_contact=True),
    ],

], resize_keyboard=True, selective=True)

st_data_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="💰 Баланс"),
        KeyboardButton(text="📅 Посещение"),
    ],
    [
        KeyboardButton(text="🔙 Главное меню"),
    ]

], resize_keyboard=True, selective=True)

confirm_button = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="✅ Да"),
        KeyboardButton(text="❌ Нет"),
    ],

], resize_keyboard=True, one_time_keyboard=True, selective=True)

def students_inline_keyboard_builder(data):
    kb = InlineKeyboardBuilder()

    for info in data:
        kb.button(text=info['text'], callback_data=info['callback_data'])

    kb.adjust(1)
    return kb.as_markup()

def subjects_inline_keyboard_builder(data):
    kb = InlineKeyboardBuilder()

    for info in data:
        kb.button(text=info['text'], callback_data=info['callback_data'])

    kb.adjust(1)
    return kb.as_markup()

def teachers_inline_keyboard_builder(data):
    kb = InlineKeyboardBuilder()

    for info in data:
        kb.button(text=info['text'], callback_data=info['callback_data'])

    kb.adjust(1)
    return kb.as_markup()