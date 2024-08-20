"""
This a test module which run some agent tests

This tests check various agent function.
WARNING! You need stable internet connection and turn on proxy server.
Also, each test requires some time to finish, so run it carefully
Run all tests:
    pytest tests/agent_tests/test.py -s -v

Run single test:
    pytest tests/agent_tests/test.py::{TEST_FUNCTION_NAME} -s -v
"""
from src.agent.main import Agent
import pytest
import json


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_query():
    agent = Agent()
    query = "Что такое криптовалюта?"
    await agent.test_query(query)


@pytest.mark.timeout(30)
@pytest.mark.asyncio
async def test_tool():
    agent = Agent()
    query = "Че щас по биткоину?"
    modify_query = await agent.test_query(query)
    tools = await agent.test_tool(modify_query)
    assert tools


@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_request():
    agent = Agent()
    query = "Че щас по биткоину?"
    response = await agent.test_greeting(query)
    print(response)
    assert len(response) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(30)
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
