import asyncio
import logging
from threading import Thread

from quart import Quart

from VK import VKDatabase, VKGroup
from TelegramBot import telegram_bot
from YouTube import youtube_blueprint, YouTubeDatabase
from Twitch import twitch_blueprint

# Базовая конфигурация для логов.
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

# Заглушить лог для кэша google-api
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)


# Запустить quart
app = Quart(__name__)

# Зарегистрировать ссылки на YouTube
app.register_blueprint(youtube_blueprint)

# Зарегистрировать ссылки на Twitch
app.register_blueprint(twitch_blueprint)


# Когда quart запущен.
@app.before_serving
async def on_start():
    # Инициализировать базу данных для видео
    await YouTubeDatabase.init_video_table()
    # Инициализировать базу данных для постов ВК
    await VKDatabase.init_posts_table()

    # Задача на фоне для проверки ВК
    app.add_background_task(VKGroup.notify_activities, telegram_bot, 60)


@app.after_serving
async def on_end():
    for task in app.background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0")
