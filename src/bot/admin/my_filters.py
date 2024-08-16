"""
This is module provide access to admin panel

Admins access providing only for admin-users. Admin-users have 1 in is_admin row in database.
Typical usage example:

    from src.bot.admin.my_filters import AdminFilter
    @router.callback_query(F.data == "admin_panel", AdminFilter())
"""
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from src.pgsqldatabase.database import Database


class AdminFilter(BaseFilter):
    database = Database()

    async def __call__(self, obj: TelegramObject):
        return obj.from_user.id in await self.database.get_all_admins_id()
