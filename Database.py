import logging
from mysql.connector import connect, Error


class Database:
    """
    Класс для общей работы с базами данных и таблицами.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Создаем экземпляр класса
            logging.info("Экземпляр базы данных создан.")
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, user: str, password: str, database: str = ""):
        self.connection = connect(
                host=host,
                user=user,
                password=password,
                port="3306",
                database=database
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Применить изменения
        self.connection.commit()
        # Закрыть курсор
        self.connection.cursor().close()
        # Закрыть соединение с базой данных
        self.connection.close()

    def execute(self, query: str, params: tuple = ()) -> list:
        try:
            # Получаем курсор для выполнения запросов
            cursor = self.connection.cursor()
            # Выполняем запрос
            cursor.execute(query, params)
            # Получаем результат запроса
            result = cursor.fetchall()
            # Закрываем курсор
            cursor.close()
            # Возвращаем результат запроса
            return result
        except Error as error:
            logging.error(f"Ошибка при выполнении запроса MYSQL: \n{error}")