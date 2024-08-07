from src.agent.main import answer
import pytest


# pytest tests/agent_tests/test.py -s -v

@pytest.mark.asyncio
@pytest.mark.timeout(10)  # Устанавливаем лимит времени в 60 секунд
async def test_hello():
    respond = await answer("Привет!")
    print(respond)
    assert len(respond) >= 1


@pytest.mark.asyncio
@pytest.mark.timeout(60)  # Устанавливаем лимит времени в 60 секунд
async def test_request():
    respond = await answer("Расскажи мне про ЛЭТИ")
    print(respond)
    assert len(respond) >= 1
