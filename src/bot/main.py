from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties

from src.bot import admin
from src.bot.handler import handler_commands, handler_messages
from src.aiopgsqldatabase.database import create_table
from config.config import config
import logging

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    token = config("config.ini", "bot_token")["token"]
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(admin.router, handler_commands.router, handler_messages.router)

    await create_table()

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
