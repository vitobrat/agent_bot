from src.agent.main import Agent
import pytest

# pytest tests/agent_tests/test.py -s -v


# @pytest.mark.timeout(10)
# @pytest.mark.asyncio
# async def test_hello():
#     query = "Привет!"
#     response = await agent.test_greeting(query)
#     assert len(response) >= 1


@pytest.mark.asyncio
async def test_request():
    agent = Agent()
    query = "Че щас творится с Биткоином?"
    response = await agent.test_greeting(query)
    print(response)
    assert len(response) >= 1


# @pytest.mark.asyncio
# @pytest.mark.timeout(10)
# async def test_sum():
#     with open("articles.json", 'r', encoding='utf-8') as file:
#         content = json.load(file)
#     response = ""
#     for key, value in content.items():
#         response = await agent.summarization(value["article"])
#         break
#     print(response)
#     assert len(response) >= 1