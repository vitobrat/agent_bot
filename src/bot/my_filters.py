from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject

admin_ids = [1044539451,]


class AdminFilter(BaseFilter):
    async def __call__(self, obj: TelegramObject):
        return obj.from_user.id in admin_ids
