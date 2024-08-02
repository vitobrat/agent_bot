import asyncpg
from config.config import config

database = config("config.ini", "postgresql")

async def create_table():
    conn = await asyncpg.connect(**database)
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            user_name TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    await conn.close()

async def get_user(user_id):
    conn = await asyncpg.connect(**database)
    row = await conn.fetchrow('''
        SELECT * FROM users WHERE user_id = $1
    ''', user_id)
    await conn.close()
    return row

async def get_all_users():
    conn = await asyncpg.connect(**database)
    rows = await conn.fetch('''
        SELECT * FROM users
    ''')
    await conn.close()
    return rows

async def add_user(user_id, user_fullname, user_username):
    conn = await asyncpg.connect(**database)
    check_user = await get_user(user_id)
    if check_user is None:
        await conn.execute('''
            INSERT INTO users (user_id, full_name, user_name, is_admin) VALUES ($1, $2, $3, $4)
        ''', user_id, user_fullname, user_username, 0)
    await conn.close()

async def count_users():
    conn = await asyncpg.connect(**database)
    count = await conn.fetchval('''
        SELECT COUNT(*) FROM users
    ''')
    await conn.close()
    return count

async def get_all_users_id():
    conn = await asyncpg.connect(**database)
    rows = await conn.fetch('''
        SELECT user_id FROM users
    ''')
    await conn.close()
    return rows
