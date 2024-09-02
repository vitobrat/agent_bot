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


async def parse_articles(today: str) -> None:
    """Parse articles from website https://ru.investing.com/news/cryptocurrency-news

    Attributes:
        today: only articles with this date are parsing
    """
    articles = Articles()
    agent = Agent()
    await parser_main(today)
    await articles.clean_old_articles()
    await articles.load()
    await agent.generate_agent_executor()


async def main() -> None:
    """Main project function

    It starts telegram bot, create database if it needed, load list of articles, configure agent and schedule parsing
    """
    today = datetime.today().strftime("%Y-%m-%d")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Take token from config file
    token = config("config.ini", "tokens")["bot_token"]

    # Initial bot
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))

    # Create dispatcher and relate it to routers
    dp = Dispatcher()
    dp.include_routers(admin.router, handler_commands.router, handler_messages.router)
    await bot.set_my_commands(commands)

    # Creat table if it not exists
    database = Database()
    await database.create_table()

    # Parse new articles
    await parser_main(today)

    # Load articles list
    articles = Articles()
    await articles.clean_old_articles()
    await articles.load()

    # Initial and configure agent
    agent = Agent()
    await agent.generate_agent_executor()

    # Initial schedule tasks
    scheduler = AsyncIOScheduler()

    # Take current tasks loop
    loop = asyncio.get_running_loop()

    # Launch parsing every hour
    scheduler.add_job(
        lambda: asyncio.run_coroutine_threadsafe(parse_articles(today), loop),
        IntervalTrigger(hours=1),
    )

    scheduler.start()

    # Start bot and miss all enter message
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
