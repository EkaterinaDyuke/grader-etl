"""Подключение к PostgreSQL и базовые операции с базой."""

import psycopg2
from psycopg2.extras import RealDictCursor # не кортежами, а словарями


class Database:
    """Одно подключение на всю программу (singleton)."""

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, host, port, database, user, password, autocommit=False):
        if hasattr(self, "connection"):
            return
        self.connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
        )
        if autocommit:
            self.connection.autocommit = True
        self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)

    def select(self, query, vars=()):
        self.cursor.execute(query, vars)
        return self.cursor.fetchall()

    def post(self, query, vars=()):
        self.cursor.execute(query, vars)
        if not self.connection.autocommit:
            self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()