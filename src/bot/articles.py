import os
import json
from datetime import datetime

form = ("Описание статьи: {0}\n"
        "Ссылка на статью: {1}\n"
        "Дата публикации: {2}\n")


class Articles:
    def __init__(self, filename: str):
        self.__list_of_all_pages = []
        self.__list_of_today_pages = []
        self.__filename = filename
        self.__page_index_all = 0
        self.__page_index_today = 0
        self.__all_articles = self.load_all_data()

    @property
    def filename(self):
        return self.__filename

    @property
    def all_articles(self):
        return self.__all_articles

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

    def load_all_data(self) -> dict:
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    async def generate_all_pages(self) -> None:
        page = []
        for i, (url, content) in enumerate(self.all_articles.items()):
            page.append(form.format(content["summarization_article"], url, content["date"]))
            if (i + 1) % 5 == 0:
                self.__list_of_all_pages.append(page)
                page = []
        if page:
            self.__list_of_all_pages.append(page)

    async def generate_today_pages(self) -> None:
        for i, (url, content) in enumerate(self.all_articles.items()):
            if content["date"] == datetime.today().strftime('%Y-%m-%d'):
                self.list_of_today_pages.append(form.format(content["summarization_article"],
                                                            url, content["date"]))
