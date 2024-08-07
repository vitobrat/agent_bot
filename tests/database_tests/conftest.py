import pytest
from src.pgsqldatabase.database import Database
import asyncio

database = Database("users_test")


@pytest.fixture(autouse=True, scope="session")
def creat_db():
    assert database.table_name == "users_test"
    asyncio.run(database.drop_all())
    asyncio.run(database.create_table())
    print("re-clear database")
