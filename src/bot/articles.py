import os
import json
from datetime import datetime, timedelta

form = ("Описание статьи: {0}\n"
        "Ссылка на статью: {1}\n"
        "Дата публикации: {2}, {3}\n")


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
            self.__all_articles = None
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

    @property
    def all_articles(self):
        return self.__all_articles

    async def load_articles(self):
        """Загружает статьи из файла."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}

    async def save_articles(self, articles):
        """Сохраняет статьи в файл."""
        if os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(articles, file, ensure_ascii=False, indent=4)

    async def load(self) -> None:
        await self.load_all_data()
        await self.generate_all_pages()
        await self.generate_today_pages()

    async def load_all_data(self):
        self.__all_articles = await self.load_articles()

    async def generate_all_pages(self) -> (None, str):
        page = []
        self.__list_of_all_pages = []
        for i, (url, content) in enumerate(reversed(self.all_articles.items())):
            page.append(form.format(content["summarization_article"], url, content["date"], content["time"]))
            if (i + 1) % 5 == 0:
                self.__list_of_all_pages.append(page)
                page = []
        if page:
            self.__list_of_all_pages.append(page)

    async def generate_today_pages(self) -> None:
        self.__list_of_today_pages = []
        for url, content in reversed(self.all_articles.items()):
            if content["date"] == datetime.today().strftime('%Y-%m-%d'):
                date = content["date"].split('-')
                self.list_of_today_pages.append(form.format(content["summarization_article"],
                                                            url, f"{date[-1]}.{date[1]}.{date[0]}", content["time"]))

    async def clean_old_articles(self, date=(datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")) -> None:
        # Преобразуем строку с датой в объект datetime для сравнения
        print("start clean old articles")
        cutoff_date = datetime.strptime(date, "%Y-%m-%d")
        articles = await self.load_articles()

        # Фильтруем статьи, оставляя только те, которые выпущены после cutoff_date
        filtered_articles = {
            url: content for url, content in articles.items()
            if datetime.strptime(content['date'], "%Y-%m-%d") > cutoff_date
        }

        # Перезаписываем файл articles.json с обновлённым списком статей
        await self.save_articles(filtered_articles)

        print(f"Articles older {date} was  been deleted successfully.")

    async def test(self, test: str) -> None:
        self.__list_of_all_pages.append(test)
        self.__list_of_today_pages.append(test)

    async def clear(self) -> None:
        self.__list_of_all_pages = []
        self.__list_of_today_pages = []
