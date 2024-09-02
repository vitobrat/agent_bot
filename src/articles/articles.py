"""
This is the method that works with the articles.json file

There is a singleton class that provide to interaction with article.json where store all information.
Typical usage example:

    from src.articles import Articles

    articles = Articles()
    await articles.clean_old_articles()  #to delete outdated data
    await articles.load()  #to load relevant data
"""
import os
import json
from datetime import datetime, timedelta

form = ("Описание статьи: {0}\n"
        "Ссылка на статью: {1}\n"
        "Дата публикации: {2}, {3}\n")


class Articles:
    """Singleton class to handle and provide list of articles.

    This class consist the same information as articles.json file to provide it to the other classes.
    It reset list_of_all_pages, list_of_today_pages,
    all_articles in this situation and json file where store parce information in further cases:
    - when bot start
    - after parsing, if the json file is changed
    - after cleaning old articles
    - after admin call

    Attributes:
        list_of_all_pages: list with summarize information of each article
        list_of_today_pages: list with summarize information of each article which was publicised today
        all_articles: dict with information as in json file
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Articles, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.__list_of_all_pages = []
            self.__list_of_today_pages = []
            self.__filename = "articles.json"
            self.__all_articles = None
            self._initialized = True

    @property
    def filename(self) -> str:
        """Returns json file name with articles"""
        return self.__filename

    @property
    def list_of_all_pages(self) -> list[str]:
        """Returns list with summarize text of news articles"""
        return self.__list_of_all_pages

    @property
    def list_of_today_pages(self) -> list[str]:
        """Returns list with summarize text of today news articles"""
        return self.__list_of_today_pages

    @property
    def all_articles(self) -> dict:
        """Returns information from json file"""
        return self.__all_articles

    async def load_articles(self) -> dict:
        """Load articles from json file

        Returns:
            dict with information as in json file
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    async def save_articles(self, articles: dict) -> None:
        """Save dict with new parse data in json file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(articles, file, ensure_ascii=False, indent=4)

    async def load(self) -> None:
        """Update all structure when information in json file is updated"""
        await self.load_all_data()
        await self.generate_all_pages()
        await self.generate_today_pages()

    async def load_all_data(self):
        self.__all_articles = await self.load_articles()

    async def generate_all_pages(self) -> None:
        """Refresh data in list with all articles"""
        page = []
        self.__list_of_all_pages = []
        for i, (url, content) in enumerate(reversed(self.all_articles.items())):
            date = content["date"].split('-')
            page.append(form.format(content["summarization_article"],
                                    url, f"{date[-1]}.{date[1]}.{date[0]}", content["time"]))
            if (i + 1) % 5 == 0:
                self.__list_of_all_pages.append(page)
                page = []
        if page:
            self.__list_of_all_pages.append(page)

    async def generate_today_pages(self) -> None:
        """Refresh data in list with today articles"""
        self.__list_of_today_pages = []
        for url, content in reversed(self.all_articles.items()):
            if content["date"] == datetime.today().strftime('%Y-%m-%d') and content["summarization_article"]:
                date = content["date"].split('-')
                self.list_of_today_pages.append(form.format(content["summarization_article"],
                                                            url, f"{date[-1]}.{date[1]}.{date[0]}", content["time"]))

    async def clean_old_articles(self, date=(datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")) -> None:
        """Clean too old articles and update json file

        Attributes:
            date: str format date (year-month-day). Older this date all articles is deleted
        """
        # Convert str date to datetime object to compare
        print("start clean old articles")
        cutoff_date = datetime.strptime(date, "%Y-%m-%d")
        articles = await self.load_articles()

        # Filter articles that have published after cutoff_date
        filtered_articles = {
            url: content for url, content in articles.items()
            if datetime.strptime(content['date'], "%Y-%m-%d") > cutoff_date
        }

        # Update json file with actual articles
        await self.save_articles(filtered_articles)

        print(f"Articles older {date} was  been deleted successfully.")

    async def test(self, test: str) -> None:
        """Function for run articles tests"""
        self.__list_of_all_pages.append(test)
        self.__list_of_today_pages.append(test)

    async def clear(self) -> None:
        """Clear lists with articles"""
        self.__list_of_all_pages = []
        self.__list_of_today_pages = []
