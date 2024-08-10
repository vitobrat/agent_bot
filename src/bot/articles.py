import os
import json
from datetime import datetime

form = ("Описание статьи: {0}\n"
        "Ссылка на статью: {1}\n"
        "Дата публикации: {2}\n")


class Articles:
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
            self.__page_index_all = 0
            self.__page_index_today = 0
            self._initialized = True

    @property
    def filename(self):
        return self.__filename

    @property
    def page_index_today(self):
        return self.__page_index_today

    async def page_index_today_start(self):
        self.__page_index_today = 0

    async def page_index_today_next(self):
        self.__page_index_today = min(self.page_index_today + 1, len(self.list_of_today_pages) - 1)

    async def page_index_today_prev(self):
        self.__page_index_today = max(self.page_index_today - 1, 0)

    @property
    def page_index_all(self):
        return self.__page_index_all

    async def page_index_all_start(self):
        self.__page_index_all = 0

    async def page_index_all_next(self):
        self.__page_index_all = min(self.page_index_all + 1, len(self.list_of_all_pages) - 1)

    async def page_index_all_prev(self):
        self.__page_index_all = max(self.page_index_all - 1, 0)

    @property
    def list_of_all_pages(self):
        return self.__list_of_all_pages

    @property
    def list_of_today_pages(self):
        return self.__list_of_today_pages

    async def load_all_data(self) -> dict:
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    async def generate_all_pages(self) -> (None, str):
        all_articles = await self.load_all_data()
        page = []
        self.__list_of_all_pages = []
        for i, (url, content) in enumerate(reversed(all_articles.items())):
            page.append(form.format(content["summarization_article"], url, content["date"]))
            if (i + 1) % 5 == 0:
                self.__list_of_all_pages.append(page)
                page = []
        if page:
            self.__list_of_all_pages.append(page)

    async def generate_today_pages(self) -> None:
        all_articles = await self.load_all_data()
        self.__list_of_today_pages = []
        for url, content in reversed(all_articles.items()):
            if content["date"] == datetime.today().strftime('%Y-%m-%d'):
                self.list_of_today_pages.append(form.format(content["summarization_article"],
                                                            url, content["date"]))

    async def test(self, test: str) -> None:
        self.__list_of_all_pages.append(test)
        self.__list_of_today_pages.append(test)

    async def clear(self) -> None:
        self.__list_of_all_pages = []
        self.__list_of_today_pages = []

