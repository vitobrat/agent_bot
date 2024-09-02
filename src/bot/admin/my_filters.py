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
    """Provide admin access"""

    database = Database()

    async def __call__(self, obj: TelegramObject) -> bool:
        """Check user to admin access (1 in database table row) and return true if it is

        Attribute:
            obj: information that provides from user query (user id and e.t.c.)

        Returns:
            true if user has user access and false if it isn't
        """
        return obj.from_user.id in await self.database.get_all_admins_id()
