import pytest
from src.agent.main import Agent
from src.bot.articles import Articles
import asyncio


@pytest.fixture(autouse=True, scope="session")
def load_articles():
    main_articles = Articles()
    asyncio.run(main_articles.load_all_data())
    agent = Agent()
    asyncio.run(agent.generate_agent_executor())
