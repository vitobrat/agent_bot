from src.agent.main import Agent
import pytest
import json


# pytest tests/agent_tests/test.py -s -v


@pytest.mark.timeout(15)
@pytest.mark.asyncio
async def test_query():
    agent = Agent()
    query = "Какие новости слышны про биткоин?"
    await agent.test_query(query)


@pytest.mark.timeout(15)
@pytest.mark.asyncio
async def test_tool():
    agent = Agent()
    query = "Какие новости слышны про биткоин?"
    modify_query = await agent.test_query(query)
    tools = await agent.test_tool(modify_query)
    assert tools


@pytest.mark.asyncio
@pytest.mark.timeout(20)
async def test_request():
    agent = Agent()
    query = "Че щас творится с Биткоином?"
    response = await agent.test_greeting(query)
    print(response)
    assert len(response) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_sum():
    agent = Agent()
    with open("articles.json", 'r', encoding='utf-8') as file:
        content = json.load(file)
    response = ""
    for key, value in content.items():
        response = await agent.summarization(value["article"])
        break
    print(response)
    assert len(response) >= 1
