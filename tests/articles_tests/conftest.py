import pytest
from src.bot.articles import Articles
import asyncio


@pytest.fixture(autouse=True, scope="session")
def load_articles():
    main_articles = Articles()
    asyncio.run(main_articles.delete_old_articles())
    asyncio.run(main_articles.load())
