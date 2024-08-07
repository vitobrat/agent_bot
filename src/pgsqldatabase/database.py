import asyncpg
from config.config import config
import re

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
        exe_command = (f"CREATE TABLE IF NOT EXISTS {self.table_name}("
                       f"user_id INTEGER PRIMARY KEY,"
                       f"full_name TEXT,"
                       f"user_name TEXT,"
                       f"is_admin INTEGER DEFAULT 0)")
        await conn.execute(exe_command)
        await conn.close()

    async def get_user(self, user_id: int):
        conn = await asyncpg.connect(**database)
        exe_command = f"SELECT * FROM {self.table_name} WHERE user_id = $1"
        row = await conn.fetchrow(exe_command, user_id)
        await conn.close()

        return row

    async def get_all_users(self):
        conn = await asyncpg.connect(**database)
        exe_command = f" SELECT * FROM {self.table_name}"
        rows = await conn.fetch(exe_command)
        await conn.close()
        return rows

    async def add_user(self, user_id, user_fullname, user_username):
        conn = await asyncpg.connect(**database)
        check_user = await self.get_user(user_id)
        if check_user is None:
            exe_command = (f"INSERT INTO {self.table_name} (user_id, full_name, user_name, is_admin) "
                           f"VALUES ($1, $2, $3, $4)")
            await conn.execute(exe_command, user_id, user_fullname, user_username, 0)
        await conn.close()

    async def count_users(self):
        conn = await asyncpg.connect(**database)
        exe_command = f"SELECT COUNT(*) FROM {self.table_name}"
        count = await conn.fetchval(exe_command)
        await conn.close()
        return count

    async def get_all_users_id(self):
        conn = await asyncpg.connect(**database)
        exe_command = f"SELECT user_id FROM {self.table_name}"
        rows = await conn.fetch(exe_command)
        await conn.close()
        return rows
