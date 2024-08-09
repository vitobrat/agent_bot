import json

from src.agent.main import Agent
import pytest

# pytest tests/agent_tests/test.py -s -v
agent = Agent()


@pytest.mark.timeout(10)
@pytest.mark.asyncio
async def test_hello():
    query = "Привет!"
    response = await agent.test_greeting(query)
    assert len(response) >= 1


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_request():
    query = "Расскажи мне про ЛЭТИ"
    response = await agent.test_greeting(query)
    assert len(response) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(10)  # Устанавливаем лимит времени в 60 секунд
async def test_sum():
    with open("articles.json", 'r', encoding='utf-8') as file:
        content = json.load(file)
    response = ""
    for key, value in content.items():
        response = await agent.summarization(value["article"])
        break
    print(response)
    assert len(response) >= 1
