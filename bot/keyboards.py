from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# def get_phone_keyboard():
#     keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
#     button = KeyboardButton(text="📱 Send my number", request_contact=True)
#     keyboard.add(button)
#     return keyboard


request_phone_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="📱 Send my number", request_contact=True),
    ],

], resize_keyboard=True, one_time_keyboard=True, selective=True)

confirm_button = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="Да"),
    ],

], resize_keyboard=True, one_time_keyboard=True, selective=True)

