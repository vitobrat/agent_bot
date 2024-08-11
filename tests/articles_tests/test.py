import pytest
from src.bot.articles import Articles


# pytest tests/articles_tests/test.py -s -v


@pytest.mark.asyncio
class TestArticles:

    async def test_generate_all(self):
        articles = Articles()
        await articles.generate_all_pages()
        assert articles.list_of_all_pages

    async def test_generate_today(self):
        articles = Articles()
        await articles.generate_today_pages()
        assert articles.list_of_today_pages

    async def test_singleton(self):
        articles = Articles()
        await articles.test("test")
        assert articles.list_of_all_pages[-1] == "test"
        assert articles.list_of_today_pages[-1] == "test"
        assert len(articles.list_of_all_pages) > 1
        assert len(articles.list_of_today_pages) > 1
        await articles.clear()
