"""
A module for handle with user database

This module do all operating with database.
It uses PostgresSql to store database and execute all operating in async mode.
It uses asyncpg library for async mode.
All secrets data to connect database store in config.ini file in postgresql section.
To obtain it, you need to parse it by config.py.
Database exist like a class, so you need initialise it in module when you use it
Typical usage example:

    from src.pgsqldatabase.database import Database

    database = Database()
"""
import json
import asyncpg
from config.config import config
import re
from src.pgsqldatabase.json_encoder import message_decoder, MessageEncoder
from src.pgsqldatabase.queries import (CREATE_TABLE_QUERY, DROP_TABLE_QUERY, COUNT_USERS_QUERY, DELETE_USER_QUERY,
                                       INSERT_USER_QUERY, GET_USER_QUERY, GET_ALL_USER_IDS_QUERY,
                                       UPDATE_USER_HISTORY_QUERY, GET_USER_HISTORY_QUERY, GET_ALL_ADMINS_ID,
                                       GET_ALL_USERS_QUERY)

database = config("config.ini", "postgresql")


class Database:
    def __init__(self, table_name="users"):
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError("Invalid table name")
        self.__table_name = table_name

    @property
    def table_name(self):
        return self.__table_name

    async def create_table(self):
        conn = await asyncpg.connect(**database)
        await conn.execute(CREATE_TABLE_QUERY.format(self.table_name))
        await conn.close()

    async def get_user(self, user_id: int):
        conn = await asyncpg.connect(**database)
        row = await conn.fetchrow(GET_USER_QUERY.format(self.table_name), user_id)
        await conn.close()
        if row:
            row = (row[0], row[1], row[2], row[3], json.loads(row[4], object_hook=message_decoder))
        return row

    async def get_all_users(self):
        conn = await asyncpg.connect(**database)
        rows = await conn.fetch(GET_ALL_USERS_QUERY.format(self.table_name))
        await conn.close()
        if rows:
            for i in range(len(rows)):
                if rows[i]:
                    rows[i] = (rows[i][0], rows[i][1], rows[i][2], rows[i][3],
                               json.loads(rows[i][4], object_hook=message_decoder))
        return rows

    async def print_all_users(self):
        return "\n".join([f"{i}) ID - {user[0]}; Full name - {user[1]}; User name - {user[2]};Is admin - {user[3]};"
                          f" History - {bool(user[4])}" for i, user in enumerate(await self.get_all_users())])

    async def add_user(self, user_id, user_fullname, user_username, is_admin=0, history=None):
        # Проверка user_id на наличие только цифр
        if history is None:
            history = []
        if not isinstance(user_id, int):
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             f"(user_id must be an integer)")

        # Проверка user_fullname и user_username на строковой тип и длину менее 100 символов
        if not isinstance(user_fullname, str) or len(user_fullname) >= 100:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(user_fullname must be a string and less than 100 characters)")

        if not isinstance(user_username, str) or len(user_username) >= 100:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(user_username must be a string and less than 100 characters)")

        # Проверка is_admin на значения 0 или 1
        if is_admin not in [0, 1]:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(is_admin must be either 0 or 1)")

        if not isinstance(history, list):
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(history must be a list)")
        conn = await asyncpg.connect(**database)
        check_user = await self.get_user(user_id)
        if check_user is None:
            await conn.execute(INSERT_USER_QUERY.format(self.table_name), user_id, user_fullname, user_username,
                               is_admin, json.dumps(history, cls=MessageEncoder))
        await conn.close()

    async def count_users(self):
        conn = await asyncpg.connect(**database)
        count = await conn.fetchval(COUNT_USERS_QUERY.format(self.table_name))
        await conn.close()
        return count

    async def get_all_users_id(self):
        conn = await asyncpg.connect(**database)
        rows = await conn.fetch(GET_ALL_USER_IDS_QUERY.format(self.table_name))
        await conn.close()
        return [user_id[0] for user_id in rows]

    async def get_all_admins_id(self) -> list:
        conn = await asyncpg.connect(**database)
        rows = await conn.fetch(GET_ALL_ADMINS_ID.format(self.table_name))
        await conn.close()
        return [user_id[0] for user_id in rows]

    async def get_user_history(self, user_id):
        conn = await asyncpg.connect(**database)
        row = await conn.fetchrow(GET_USER_HISTORY_QUERY.format(self.table_name), user_id)
        await conn.close()
        if row is None or row['history'] is None:
            return []
        return json.loads(row['history'], object_hook=message_decoder)

    async def update_user_history(self, user_id, new_history=None):
        if new_history is None:
            new_history = []
        conn = await asyncpg.connect(**database)
        await conn.fetchrow(UPDATE_USER_HISTORY_QUERY.format(self.table_name), user_id,
                            json.dumps(new_history, cls=MessageEncoder))
        await conn.close()

    async def delete_all(self):
        conn = await asyncpg.connect(**database)
        await conn.fetch(DELETE_USER_QUERY.format(self.table_name))
        await conn.close()

    async def drop_all(self):
        conn = await asyncpg.connect(**database)
        await conn.fetch(DROP_TABLE_QUERY.format(self.table_name))
        await conn.close()
