import logging
import os

from quart import Blueprint, request, jsonify
from TelegramBot import telegram_bot

twitch_blueprint = Blueprint("twitch", __name__)

twitch_link: str = "https://www.twitch.tv/elwycco"

@twitch_blueprint.route("/callback", methods=["POST", "GET"])
async def twitch():
    data = await request.get_json()

    logging.info("Получен ответ от twitch.")

    # Если запрос содержит в себе задачу подписаться
    message_type = request.headers.get("twitch-eventsub-message-type")
    if message_type == 'webhook_callback_verification':
        notification = await request.get_json()
        total = notification["challenge"]
        return total, 200, {'Content-Type': 'text/plain'}

    # Если ответ с данными содержит 'event', то уведомить подписчиков
    stream_event = data and data.get("event")
    if stream_event:
        await telegram_bot.send_message(os.environ["GROUP_ID"], f"⚡️Стрим начался! {twitch_link}")

    # handle the callback data here
    return jsonify({"status": "OK"}), 200
