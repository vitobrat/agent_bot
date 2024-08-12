from aiogram import Bot, Dispatcher
import asyncio

from aiogram.client.default import DefaultBotProperties

from src.bot import admin
from src.bot.handler import handler_commands, handler_messages
from src.pgsqldatabase.database import Database
from config.config import config
import logging
from src.bot.articles import Articles
from src.agent.main import Agent


logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    token = config("config.ini", "tokens")["bot_token"]
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(admin.router, handler_commands.router, handler_messages.router)

    database = Database()
    await database.create_table()

    articles = Articles()
    await articles.load_all_data()
    await articles.generate_all_pages()
    await articles.generate_today_pages()

    agent = Agent()
    await agent.generate_agent_executor()

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
