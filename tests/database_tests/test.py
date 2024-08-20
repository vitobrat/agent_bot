"""
This tests check each database function.

Run all tests:
    pytest tests/database_tests/test.py -s -v

Run single test:
    pytest tests/database_tests/test.py::TestUsers::{TEST_FUNCTION_NAME} -s -v
"""
import pytest
from src.pgsqldatabase.database import Database
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage


# pytest tests/database_tests/test.py -s -v


@pytest.fixture
def users():
    users = [
        (1, "full_name1", "username1", 0, []),
        (2, "full_name2", "username2", 0, [
            SystemMessage(content="you're a good assistant"),
            HumanMessage(content="hi! I'm bob"),
            AIMessage(content="hi!"),
            HumanMessage(content="I like vanilla ice cream"),
            AIMessage(content="nice")]),
        (3, "full_name4", "username4", 1, []),
        (1, "full_name1", "username1", 0, [])
    ]
    return users


@pytest.mark.asyncio
class TestUsers:
    database = Database("users_test")

    async def test_add_users(self, users):
        for user in users:
            await self.database.add_user(user[0], user[1], user[2], user[3], user[4])
        assert await self.database.get_all_users_id() == [1, 2, 3]

    async def test_incorrect_add_user1(self):
        with pytest.raises(ValueError):
            await self.database.add_user("id", "full_name_test",
                                         "username_test", 0)

    async def test_incorrect_add_user2(self):
        with pytest.raises(ValueError):
            await self.database.add_user(4, 5,
                                         "username_test", 0)

    async def test_incorrect_add_user3(self):
        with pytest.raises(ValueError):
            await self.database.add_user(4, "full_name_test",
                                         "username_test" * 10, 0)

    async def test_incorrect_add_user4(self):
        with pytest.raises(ValueError):
            await self.database.add_user(4, "full_name_test",
                                         "username_test", 2)

    async def test_count_users(self):
        assert await self.database.count_users() == 3

    async def test_get_user(self, users):
        assert await self.database.get_user(2) == users[1]

    async def test_get_all_users(self, users):
        assert await self.database.get_all_users() == users[:-1]

    async def test_get_all_users_id(self, users):
        assert await self.database.get_all_users_id() == [1, 2, 3]

    async def test_get_user_history(self, users):
        assert await self.database.get_user_history(2) == users[1][-1]

    async def test_update_user_history(self, users):
        await self.database.update_user_history(2, [])
        assert await self.database.get_user_history(2) == []
        await self.database.update_user_history(1, [
            SystemMessage(content="you're a good assistant"),
            HumanMessage(content="hi! I'm bob"),
            AIMessage(content="hi!"),
            HumanMessage(content="I like vanilla ice cream"),
            AIMessage(content="nice"),
            HumanMessage(content="whats 2 + 2"),
            AIMessage(content="4"),
            HumanMessage(content="thanks"),
            AIMessage(content="no problem!"),
            HumanMessage(content="having fun?"),
            AIMessage(content="yes!")])
        assert await self.database.get_user_history(1) == [
            SystemMessage(content="you're a good assistant"),
            HumanMessage(content="hi! I'm bob"),
            AIMessage(content="hi!"),
            HumanMessage(content="I like vanilla ice cream"),
            AIMessage(content="nice"),
            HumanMessage(content="whats 2 + 2"),
            AIMessage(content="4"),
            HumanMessage(content="thanks"),
            AIMessage(content="no problem!"),
            HumanMessage(content="having fun?"),
            AIMessage(content="yes!")]

    async def test_delete_all_users(self, users):
        await self.database.delete_all()
        assert await self.database.count_users() == 0
        assert await self.database.get_all_users() == []
        assert await self.database.get_all_users_id() == []
        assert await self.database.get_all_users() == []
        assert await self.database.get_user(1) is None
        assert await self.database.get_user_history(1) == []
