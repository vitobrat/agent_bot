"""
This is the main module in which the whole project is realised

This module start the bot, parsing articles, refresh store, handle routers and launch all another work.
When bot start, it creates (if it needs) database, parsing new articles,
load it to the store and generate agent execution. Then the articles parsing is implemented in auto mode.
To start the bot you should run expectly this file: poetry run python -m src.bot.main
"""
from aiogram import Bot, Dispatcher
import asyncio
from datetime import datetime
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import logging
from config.config import config
from src.bot.handler import handler_commands, handler_messages
from src.pgsqldatabase.database import Database
from src.articles.articles import Articles
from src.agent.main import Agent
from src.bot.keyboards import commands
from src.parser.main import main as parser_main
from src.bot.admin import admin

logger = logging.getLogger(__name__)


async def parse_articles(today: str):
    articles = Articles()
    agent = Agent()
    await parser_main(today)
    await articles.load()
    await agent.generate_agent_executor()


async def clean_articles():
    articles = Articles()
    agent = Agent()
    await articles.clean_old_articles()
    await articles.load()
    await agent.generate_agent_executor()


async def main() -> None:
    today = datetime.today().strftime('%Y-%m-%d')
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")
    token = config("config.ini", "tokens")["bot_token"]
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_routers(admin.router, handler_commands.router, handler_messages.router)
    await bot.set_my_commands(commands)

    database = Database()
    await database.create_table()

    await parser_main(today)

    articles = Articles()
    await articles.clean_old_articles()
    await articles.load()

    agent = Agent()
    await agent.generate_agent_executor()

    # Устанавливаем планировщик задач
    scheduler = AsyncIOScheduler()

    # Получаем текущий цикл событий
    loop = asyncio.get_running_loop()

    # Запускать каждый час
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(parse_articles(today), loop), IntervalTrigger(hours=1))

    # Запускать ежедневно в 00:05
    scheduler.add_job(lambda: asyncio.run_coroutine_threadsafe(clean_articles(), loop), CronTrigger(hour=0, minute=5))

    scheduler.start()

    # Запускаем бота и пропускаем все накопленные входящие
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
