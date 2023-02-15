import logging
import os

from Database import Database

class VKDatabase:
    """
    Класс для работы с таблицей и данными для постов ВК.
    """

    # Название стандартной таблицы для постов
    _vk_table_name = "vk_posts"

    @classmethod
    async def init_posts_table(cls):
        """
        Создать таблицу для хранения постов из ВК;
        :return:
        """
        logging.debug("Инициализация таблицы для постов ВК.")

        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            db.execute(f'''CREATE TABLE IF NOT EXISTS {cls._vk_table_name}(
                    post_id INT NOT NULL,
                    post_date TIMESTAMP NOT NULL,
                    PRIMARY KEY (post_id));''')

            logging.debug("Таблица для хранения постов инициализирована.")

    @classmethod
    async def find_posts_by_id(cls, posts: list) -> dict:
        """
        Найти посты по идентификаторам и вернуть те, что есть в базе данных.
        :param posts: Лист с постами в виде ["id", ...]
        :return: Словарь с результатами
        """
        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            post_placeholders = ', '.join(['%s'] * len(posts))

            r = db.execute(f"SELECT post_id, post_date FROM {cls._vk_table_name} WHERE post_id IN ({post_placeholders})",
                           (*posts,))
            results: list = [] if r is None else r
            results: dict = {i[0]: i[1] for i in results}

            return results

    @classmethod
    async def insert_post(cls, post_id: str, post_date: str):
        """
        Вставить новый пост в базу данных.
        :param post_id: Идентификатор поста.
        :param post_date: Дата публикации поста.
        :return:
        """
        with Database(os.environ["MYSQL_HOST"], os.environ["MYSQL_USER"], os.environ["MYSQL_PASSWORD"], "Wycc") as db:
            db.execute(f"INSERT INTO {cls._vk_table_name}(post_id, post_date) SELECT %s, %s",
                       (post_id, post_date))