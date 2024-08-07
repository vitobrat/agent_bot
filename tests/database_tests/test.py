import pytest
from src.pgsqldatabase.database import Database
import asyncio
# pytest tests/database_tests/test.py -s -v
database = Database("users_test")


@pytest.fixture
def users():
    users = [
        (1, "full_name1", "username1", 0),
        (2, "full_name2", "username2", 0),
        (3, "full_name4", "username4", 1),
        (1, "full_name1", "username1", 0)
    ]
    return users


class TestUsers:
    def test_add_users(self, users):
        for user in users:
            asyncio.run(database.add_user(user[0], user[1], user[2], user[3]))
        assert asyncio.run(database.get_all_users_id()) == [1, 2, 3]

    def test_incorrect_add_user1(self):
        with pytest.raises(ValueError):
            asyncio.run(database.add_user("id", "full_name_test",
                                          "username_test", 0))

    def test_incorrect_add_user2(self):
        with pytest.raises(ValueError):
            asyncio.run(database.add_user(4, 5,
                                          "username_test", 0))

    def test_incorrect_add_user3(self):
        with pytest.raises(ValueError):
            asyncio.run(database.add_user(4, "full_name_test",
                                          "username_test" * 10, 0))

    def test_incorrect_add_user4(self):
        with pytest.raises(ValueError):
            asyncio.run(database.add_user(4, "full_name_test",
                                          "username_test", 2))

    def test_count_users(self):
        assert asyncio.run(database.count_users()) == 3

    def test_get_user(self, users):
        assert asyncio.run(database.get_user(2)) == users[1]

    def test_get_all_users(self, users):
        assert asyncio.run(database.get_all_users()) == users[:-1]

    def test_get_all_users_id(self, users):
        assert asyncio.run(database.get_all_users_id()) == [1, 2, 3]

    def test_delete_all_users(self, users):
        asyncio.run(database.delete_all())
        assert asyncio.run(database.count_users()) == 0
        assert asyncio.run(database.get_all_users()) == []
        assert asyncio.run(database.get_all_users_id()) == []
        assert asyncio.run(database.get_all_users()) == []
        assert asyncio.run(database.get_user(1)) is None






