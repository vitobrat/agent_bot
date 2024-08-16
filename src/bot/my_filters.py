from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from src.pgsqldatabase.database import Database

database = Database()


class AdminFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject):
        return obj.from_user.id in await database.get_all_admins()
