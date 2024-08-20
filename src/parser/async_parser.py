"""
This a method where executing parsing articles

The parser open the main page in async mode by aiohttp and use bs4 for parsing.
There is one class which utilised only in parser.main.py
Typical usage example:
    from src.parser.async_parser import AsyncParser

    parser = AsyncParser(target_date)
"""
from bs4 import BeautifulSoup
import aiohttp
from config.config import config


class AsyncParser:
    def __init__(self, date):
        self.__date = date
        self.__data = {"urls": [],
                       "articles": [],
                       "date": [],
                       "time": []}
        self.__articles_url = config("config.ini", "urls")["articles_url"]

    @property
    def date(self):
        return self.__date

    @property
    def data(self):
        return self.__data

    @property
    def articles_url(self):
        return self.__articles_url

    @staticmethod
    async def fetch_article(session, url: str) -> str:
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                article = ""
                for element in soup.find_all(['p', "blockquote"]):
                    text = element.get_text()
                    text += "\n"
                    article += text

                return article
            else:
                print(f"Failed to retrieve page, status code: {response.status}")
                return ""

    async def fetch_urls(self, session):
        async with session.get(self.articles_url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            for article in soup.find_all("article", {"data-test": "article-item"}):
                # Ищем время публикации
                time_element = article.find("time", {"data-test": "article-publish-date"})
                if time_element:
                    # Получаем дату из атрибута dateTime
                    article_date = time_element["datetime"].split(" ")[0]

                    # Сравниваем дату с целевой
                    if article_date == self.date:
                        # Если даты совпадают, то получаем ссылку на статью
                        link = article.find("a", {"data-test": "article-title-link"})
                        if link and "href" in link.attrs:
                            self.data["urls"].append(link["href"])
                            self.data["articles"].append(await self.fetch_article(session, link["href"]))
                            self.data["date"].append(article_date)
                            self.data["time"].append(time_element["datetime"].split(" ")[-1])

    async def parse(self):
        async with aiohttp.ClientSession() as session:
            await self.fetch_urls(session)
            return self.data
