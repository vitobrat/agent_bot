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
    """For interaction with database"""
    def __init__(self, table_name="users"):
        """Initial database table name
        
        Attributes:
            table_name: database table name, by default main name "users", also can be "test" for run tests
        """
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError("Invalid table name")
        self.__table_name = table_name

    @property
    def table_name(self) -> str:
        """Returns database table name"""
        return self.__table_name

    async def create_table(self) -> None:
        """Create database table if it not exists yet"""
        conn = await asyncpg.connect(**database)
        await conn.execute(CREATE_TABLE_QUERY.format(self.table_name))
        await conn.close()

    async def get_user(self, user_id: int) -> set:
        """Get all information about user by id

        Attributes:
            user_id: integer num

        Returns:
            set with len 5, where set[0] is id, set[1] is user full name, set[2] is telegram username,
            set[3] is 1 or 0 (1 is mean user admin, 0 is not), set[4] is dialog history
        """
        conn = await asyncpg.connect(**database)
        row = await conn.fetchrow(GET_USER_QUERY.format(self.table_name), user_id)
        await conn.close()
        if row:
            row = (row[0], row[1], row[2], row[3], json.loads(row[4], object_hook=message_decoder))
        return row

    async def get_all_users(self) -> list[set]:
        """Get all information about all users

        Returns:
              list with len equal users count, list consist sets with len 5, where set[0] is id,
              set[1] is user full name, set[2] is telegram username,
              set[3] is 1 or 0 (1 is mean user admin, 0 is not), set[4] is dialog history
        """
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
        """Get beautiful output of all users. Uses information from get_all_users

        Returns:
            string with information about all users. Applies for admin panel.

        Example output:
            Users: 0) ID - ***; Full name - ***; Username - ***;Is admin - 0; History - True
            1) ID - ***; Full name - ***; Username - ***;Is admin - 0; History - False
        """
        return "\n".join([f"{i}) ID - {user[0]}; Full name - {user[1]}; Username - {user[2]};Is admin - {user[3]};"
                          f" History - {bool(user[4])}" for i, user in enumerate(await self.get_all_users())])

    async def add_user(self, user_id: int, user_fullname: str, user_username: str, is_admin=0, history=None) -> None:
        """Check and insert new user in database

        Attributes:
            user_id: user telegram id
            user_fullname: user telegram fullname
            user_username: user telegram username
            is_admin: 0 - not admin, 1 - admin
            history: dialog history in telegram
        """
        if history is None:
            history = []
        # Check that user id consists only numbers
        if not isinstance(user_id, int):
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             f"(user_id must be an integer)")

        # Check user_fullname and user_username are string and have len less 100
        if not isinstance(user_fullname, str) or len(user_fullname) >= 100:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(user_fullname must be a string and less than 100 characters)")
        if not isinstance(user_username, str) or len(user_username) >= 100:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(user_username must be a string and less than 100 characters)")

        # Check is_admin is 0 or 1
        if is_admin not in [0, 1]:
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(is_admin must be either 0 or 1)")
        
        # Check history is list
        if not isinstance(history, list):
            raise ValueError(f"Attempt to write in database incorrect user: {user_id}|{user_fullname}|{user_username}|"
                             f"{is_admin}|{history}"
                             "(history must be a list)")
        # If all correct, then add user to database
        conn = await asyncpg.connect(**database)
        check_user = await self.get_user(user_id)
        if check_user is None:
            await conn.execute(INSERT_USER_QUERY.format(self.table_name), user_id, user_fullname, user_username,
                               is_admin, json.dumps(history, cls=MessageEncoder))
        await conn.close()

    async def count_users(self) -> int:
        """Get users count

        Returns:
            the integer value means users count
        """
        conn = await asyncpg.connect(**database)
        count = await conn.fetchval(COUNT_USERS_QUERY.format(self.table_name))
        await conn.close()
        return count

    async def get_all_users_id(self) -> list[int]:
        """Get all user telegram id from database

        Returns:
            list with len equal number of users. The list consist integer users id
        """
        conn = await asyncpg.connect(**database)
        rows = await conn.fetch(GET_ALL_USER_IDS_QUERY.format(self.table_name))
        await conn.close()
        return [user_id[0] for user_id in rows]

    async def get_all_admins_id(self) -> list[int]:
        """Get all users id which is admin

        Returns:
            list of ids users which consist 1 in is_admin row
        """
        conn = await asyncpg.connect(**database)
        rows = await conn.fetch(GET_ALL_ADMINS_ID.format(self.table_name))
        await conn.close()
        return [user_id[0] for user_id in rows]

    async def get_user_history(self, user_id: int) -> list:
        """Get user dialog history with LLM
        
        Attributes:
            user_id: user telegram id
            
        Returns:
            list of LangChain "HumanMessage" - user query or "AIMessage" - LLM response
        """
        conn = await asyncpg.connect(**database)
        row = await conn.fetchrow(GET_USER_HISTORY_QUERY.format(self.table_name), user_id)
        await conn.close()
        if row is None or row['history'] is None:
            return []
        return json.loads(row['history'], object_hook=message_decoder)

    async def update_user_history(self, user_id: int, new_history=None) -> None:
        """Update user history after each LLM response by user id

        Attributes:
            user_id: user telegram id
            new_history: list of new dialog history
        """
        if new_history is None:
            new_history = []
        conn = await asyncpg.connect(**database)
        await conn.fetchrow(UPDATE_USER_HISTORY_QUERY.format(self.table_name), user_id,
                            json.dumps(new_history, cls=MessageEncoder))
        await conn.close()

    async def delete_all(self) -> None:
        """Clear database table"""
        conn = await asyncpg.connect(**database)
        await conn.fetch(DELETE_USER_QUERY.format(self.table_name))
        await conn.close()

    async def drop_all(self) -> None:
        """Drop database table"""
        conn = await asyncpg.connect(**database)
        await conn.fetch(DROP_TABLE_QUERY.format(self.table_name))
        await conn.close()
