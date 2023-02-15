import os

from aiogram import Bot

# Зарегистрировать в памяти бота для обращения к API Телеграма.
telegram_bot: Bot = Bot(token=os.environ["BOT_TOKEN"])