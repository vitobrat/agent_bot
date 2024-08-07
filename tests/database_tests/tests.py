import pytest
from src.pgsqldatabase.database import Database


@pytest.fixture(autouse=True)
def creat_db():
