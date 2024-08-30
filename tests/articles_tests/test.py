"""
This a test module which run tests relate articles

All information about articles consist in articles.json file and this tests check correct work with this file.
WARNING! If there aren't today articles, the tests test_generate_today test_singleton won't work
Run all tests:
    pytest tests/articles_tests/test.py -s -v

Run single test:
    pytest tests/articles_tests/test.py::TestArticles::{TEST_FUNCTION_NAME} -s -v
"""
import pytest
from src.articles.articles import Articles
from datetime import datetime, timedelta
from src.articles.user import User, UsersIds


@pytest.mark.asyncio
class TestArticles:
    """There are all tests relate with articles"""

    async def test_del_articles(self):
        """Add old article in json file and then delete it"""
        seven_days_ago = datetime.today() - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d")

        articles = Articles()

        # add old test article
        articles.all_articles["test"] = {
            "article": "Happycoin.club",
            "date": seven_days_ago_str,
            "time": "04:05:20",
            "summarization_article": "Компания MicroStrategy",
            "english_article": "Happycoin.club"
        }

        # save it in json file
        await articles.save_articles(articles.all_articles)

        # check that test article is added
        loaded_articles = await articles.load_articles()
        assert "test" in loaded_articles

        # delete old test article (the function which we test)
        await articles.clean_old_articles(seven_days_ago_str)

        # check that test article is deleted
        updated_articles = await articles.load_articles()
        assert "test" not in updated_articles

    async def test_user(self):
        """Test user behavior in bot
        Create 4 users and simulate that they switch articles pages.
        """
        users_id = UsersIds()
        users_id.append(User(1))
        users_id.append(User(2))
        users_id.append(User(3))
        user = users_id.find_user(1)
        if user is None:
            user = User(1)
        assert user == User(1)
        await user.page_index_all_next()
        assert user.page_index_all == 1
        user = users_id.find_user(2)
        if user is None:
            user = User(2)
        assert user == User(2)
        await user.page_index_all_prev()
        assert user.page_index_all == 0
        user = users_id.find_user(4)
        if user is None:
            user = User(4)
        assert user == User(4)
        await user.page_index_all_start()
        assert user.page_index_all == 0

    async def test_singleton(self):
        """Test that new object articles already consist list_of_all_pages and list_of_today_pages"""
        articles = Articles()
        await articles.test("test")
        assert articles.list_of_all_pages[-1] == "test"
        assert articles.list_of_today_pages[-1] == "test"
        assert len(articles.list_of_all_pages) > 1
        assert len(articles.list_of_today_pages) > 1
        await articles.clear()


