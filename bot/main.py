import types

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart, BotCommand
import asyncio
from decouple import config
import django, os
# Setup django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from .keyboards import request_phone_keyboard
from .handlers import  greeting, get_contact, confirm_contact
from .utils import RegistrationForm

from students.models import Enrollment

async def set_commands(bot: Bot):
    public_commands = [
        BotCommand(command='start', description='Запустить бот'),
        BotCommand(command='help', description="Помошь"),
    ]

    await bot.set_my_commands(commands=public_commands)

async def start():
    dp = Dispatcher()
    bot = Bot(token=config("TELEGRAM_BOT_TOKEN"))
    await set_commands(bot)

    dp.message.register(greeting, CommandStart())
    dp.message.register(get_contact, F.contact, RegistrationForm.get_phone)
    dp.message.register(confirm_contact, RegistrationForm.confirm)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())