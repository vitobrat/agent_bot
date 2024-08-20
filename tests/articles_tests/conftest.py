import pytest
from src.articles.articles import Articles
import asyncio


@pytest.fixture(autouse=True, scope="session")
def load_articles():
    main_articles = Articles()
    asyncio.run(main_articles.clean_old_articles())
    asyncio.run(main_articles.load())
