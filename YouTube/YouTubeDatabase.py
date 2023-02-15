import logging
import os

from Database import Database

class YouTubeDatabase:
    """
    Класс для хранения и работы с данными с YouTube.
    """

    # Название таблицы для хранения видео
    _youtube_table = "youtube_videos"

    @classmethod
    async def init_video_table(cls):
        logging.debug("Инициализация таблицы для хранения данных о видео.")

        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            db.execute(f'''CREATE TABLE IF NOT EXISTS {cls._youtube_table}(
                        video_id varchar(32) NOT NULL,
                        video_date TIMESTAMP NOT NULL,
                        PRIMARY KEY (video_id));''')

            logging.debug("Таблица для хранения видео инициализирована.")

    @classmethod
    async def find_video_by_id(cls, video_id: str) -> dict:
        """
        Найти видео в базе данных по ID.
        :param video_id: Строка с video_id.
        :return: Словарь с видео, либо пустой словарь.
        """
        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            r = db.execute(f"SELECT * FROM {cls._youtube_table} WHERE video_id = %s;", (video_id,))
            results: list = [] if r is None else r
            results: dict = {i[0]: i[1] for i in results}

            return results

    @classmethod
    async def insert_video(cls, video_id: str, video_date: str):
        """
        Вставить новый пост в базу данных.
        :param video_id: Идентификатор поста.
        :param video_date: Дата публикации поста.
        :return:
        """
        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            db.execute(f"INSERT INTO {cls._youtube_table}(video_id, video_date) SELECT %s, %s;", (video_id, video_date))