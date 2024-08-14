import pytest
from src.bot.articles import Articles
from datetime import datetime, timedelta


# pytest tests/articles_tests/test.py -s -v


@pytest.mark.asyncio
class TestArticles:

    async def test_generate_all(self):
        articles = Articles()
        assert articles.list_of_all_pages

    # async def test_generate_today(self):
    #     articles = Articles()
    #     assert articles.list_of_today_pages

    async def test_del_articles(self):
        seven_days_ago = datetime.today() - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.strftime("%Y-%m-%d")

        # Инициализируем класс Articles
        articles = Articles()

        # Добавляем тестовую статью
        articles.all_articles["test"] = {
            "article": "Happycoin.club",
            "date": seven_days_ago_str,
            "time": "04:05:20",
            "summarization_article": "Компания MicroStrategy",
            "english_article": "Happycoin.club"
        }

        # Сохраняем статьи в файл
        await articles.save_articles(articles.all_articles)

        # Проверяем, что тестовая статья добавлена
        loaded_articles = await articles.load_articles()
        assert "test" in loaded_articles

        # Удаляем старые статьи
        await articles.clean_old_articles(seven_days_ago_str)

        # Проверяем, что статья была удалена
        updated_articles = await articles.load_articles()
        assert "test" not in updated_articles

    async def test_singleton(self):
        articles = Articles()
        await articles.test("test")
        assert articles.list_of_all_pages[-1] == "test"
        assert articles.list_of_today_pages[-1] == "test"
        assert len(articles.list_of_all_pages) > 1
        # assert len(articles.list_of_today_pages) > 1
        await articles.clear()
