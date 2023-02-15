import asyncio
import logging
import os
import re
from datetime import datetime, date
from weakref import WeakValueDictionary
from aiogram import Bot
from vk_api import vk_api
from VK import VKDatabase
from Twitch import twitch_link


class VKGroup:
    # Ссылка на страницу группы в ВК
    vk_group_link: str = "https://vk.com/official_group_by_wycc220"

    # Идентификатор группы в ВК
    vk_group_id: str = os.environ["VK_GROUP_ID"]

    # Паттерны для поиска анонсов
    vk_wall_patterns: list = [
        re.compile(u"подруб"),
        re.compile(u"стрим"),
        re.compile(u"анонс"),
        re.compile("twitch")
    ]

    # Временный буфер постов, чтобы не проверять их наличие в БД.
    vk_posts_buffer: list = []

    # Доступ к сессии VK
    vk_session: vk_api.VkApiMethod = vk_api.VkApi(token=os.environ["VK_TOKEN"]).get_api()

    @classmethod
    async def get_wall_announces(cls, amount: int = 5) -> list:
        """
        Метод для получения списка последних анонсов со стены группы ВК.
        :param amount: Количество последних анонсов со стены.
        :return list: Список с полученными анонсами.
        """
        # Ограничение, чтобы нельзя было вернуть более 5 последних постов.
        amount = min(amount, 5)

        # Список анонсов, который будет возвращён.
        announces: list = []

        # Вернуть список последних постов в группе
        posts: WeakValueDictionary = cls.vk_session.wall.get(owner_id=cls.vk_group_id, count=amount)

        # Собрать нужные посты из группы ВК
        for post in posts["items"]:
            post_id: str = post["id"]
            post_text: str = re.sub("\n", " ", post["text"].strip())
            post_timestamp: float = post["date"]

            patterns: list = list(filter(lambda pattern: re.search(pattern, post_text.lower()), cls.vk_wall_patterns))
            if patterns:
                announces.append({
                    "post_id": post_id,
                    "post_text": post_text,
                    "post_date": datetime.fromtimestamp(post_timestamp)
                })

        return announces
        # noqa

    @classmethod
    async def get_new_activities(cls, amount: int = 5) -> list:
        """
        Получить список последней активности с анонсами на стене ВК.
        :param amount: Максимальное количество анонсов.
        :return: Лист с актуальными анонсами.
        """
        # Полночь по Минску
        midnight: datetime = datetime.combine(date.today(), datetime.min.time())

        # Итоговый список анонсов
        activities = []

        # Найти последние 5 анонсов
        posts: list = await cls.get_wall_announces(amount)

        # Получить из анонсов ID всех подходящих постов, если их нет в буфере
        # Это исключает необходимость постоянных запросов к БД, если пост уже есть в памяти
        post_ids = [post.get("post_id") for post in posts if post.get("post_id") not in cls.vk_posts_buffer]

        # Если вообще посты не найдены, то просто отправить пустой лист.
        if not post_ids:
            return activities

        # Найти список этих постов в базе данных.
        posts_from_database: dict = await VKDatabase.find_posts_by_id(post_ids)

        for post in posts:
            post_id = post.get("post_id")
            post_date = post.get("post_date")

            # Если пост не в базе данных и дата больше, чем полночь
            if post_id not in posts_from_database and post_date >= midnight:
                # То вставить пост в базу данных и список активностей
                await VKDatabase.insert_post(post_id, post_date)
                activities.append(post)
                if post_id not in cls.vk_posts_buffer:
                    cls.vk_posts_buffer.append(post_id)

        return activities
        # noqa

    @staticmethod
    async def notify_activities(bot: Bot, interval: int = 300):
        """
        Отправить уведомление о новых анонсах в группу Телеграм.
        :param bot: API бота Телеграм.
        :param interval: Интервал до следующей проверки.
        :return:
        """

        while True:
            try:
                announces = await VKGroup.get_new_activities()
                for announce in announces:
                    text = announce.get("post_text")
                    # Если в посте нет ссылки на твич, то добавить её.
                    text = text if re.search("twitch", text) else f"{text}\n{twitch_link}"

                    await bot.send_message(os.environ["TG_GROUP_ID"], f"\n{text}")
            except Exception as ex:
                logging.error(f"ОШИБКА: {ex}")

            await asyncio.sleep(interval)
