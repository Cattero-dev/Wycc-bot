import os

import feedparser
import logging
import requests

from quart import Blueprint, request, jsonify
from TelegramBot import telegram_bot
from .YouTubeDatabase import YouTubeDatabase

# Чертёж с путями для youtube
youtube_blueprint = Blueprint("youtube", __name__)

# Буфер с видео
videos_buffer: list = []


@youtube_blueprint.route("/youtube", methods=["GET", "POST"])
async def youtube():
    # получить ответ
    data = await request.get_data()
    # feedparser собирает данные из XML-ответа
    data = feedparser.parse(data)
    # Данные о выбранных видео в entries
    entries: dict = data and len(data.get("entries")) > 0 and data.get("entries")[0]

    # Если данные не пустые и индекс видео нет в буфере
    if isinstance(entries, dict) and entries["yt_videoid"] not in videos_buffer:
        # Уникальный ID видео
        video_id: str = entries["yt_videoid"]

        # Если видео нет в базе данных, то вернуть словарь с информацией
        videos_database: dict = await YouTubeDatabase.find_video_by_id(video_id)

        # Если видео нет в базе данных
        if video_id not in videos_database:
            # Ссылка на видео
            link = entries["link"]

            logging.info(f"Опубликовано новое видео: {link}")

            # Уведомить подписчиков нужной группы о новом видео
            await telegram_bot.send_message(os.environ["GROUP_ID"], link)
            await telegram_bot.get_updates()

            # Отправить в буфер
            videos_buffer.append(video_id)

            # Подписаться заново
            await youtube_resubscribe()

    # В случае необходимости подписаться на обновления
    challenge = request.args.get('hub.challenge')
    if challenge:
        return challenge

    # В любом другом случае вернуть тут 200
    return jsonify({"status": "OK"}), 200


async def youtube_resubscribe():
    response = requests.post("https://pubsubhubbub.appspot.com/", data={
        'hub.mode': 'subscribe',
        'hub.callback': 'https://cattero.dev/youtube',
        'hub.topic': f'https://www.youtube.com/xml/feeds/videos.xml?channel_id={os.environ["YOUTUBE_ID"]}',
        'hub.verify': 'async',
        'hub.verify_token': os.environ["RESUB_TOKEN"]
    })
    feed = feedparser.parse(response.text)

    if feed.status == 200 and feed.entries[0].title == 'Verification Request Succeeded':
        logging.debug("Subscription to hub extended.")
    else:
        logging.error(f"Error subscribing to the topic")