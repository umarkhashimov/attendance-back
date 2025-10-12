# Setup django
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters.command import CommandStart, BotCommand
import asyncio
from decouple import config
from .handlers import router

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

    dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start())