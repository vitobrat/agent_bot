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
    """Parsing data from website"""

    def __init__(self, date):
        """Initialize object for parsing.

        Args:
            date: target parsing date
        """
        self.__date = date
        self.__data = {"urls": [], "articles": [], "date": [], "time": []}
        self.__articles_url = config("config.ini", "urls")["articles_url"]

    @property
    def date(self):
        """Returns target parsing date"""
        return self.__date

    @property
    def data(self):
        """Returns dict with parse data"""
        return self.__data

    @property
    def articles_url(self):
        """Returns website urls from we're parsing"""
        return self.__articles_url

    @staticmethod
    async def fetch_article(session, url: str) -> str:
        """Parsing all text from website

        Attributes:
            session: async context manager for http request
            url: url website we have to parse information

        Returns:
            article text
        """
        async with session.get(url) as response:
            if response.status == 200:
                soup = BeautifulSoup(await response.text(), "html.parser")
                article = ""
                for element in soup.find_all(["p", "blockquote"]):
                    text = element.get_text()
                    text += "\n"
                    article += text

                return article
            else:
                print(f"Failed to retrieve page, status code: {response.status}")
                return ""

    async def fetch_urls(self, session):
        """Parsing articles with target date.

        It makes dict to provide it to json file. Dict form example:
             {"urls": [],
               "articles": [],
               "date": [],
               "time": []}
        So it put all information of certain article in same index of list.
        When we will read it dict, in each iterate we will bring one parce article

        Attributes:
            session: async context manager for http request
        """
        async with session.get(self.articles_url) as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            for article in soup.find_all("article", {"data-test": "article-item"}):
                # Search published time
                time_element = article.find(
                    "time", {"data-test": "article-publish-date"}
                )
                if time_element:
                    # Получаем дату из атрибута dateTime
                    article_date = time_element["datetime"].split(" ")[0]

                    # Compare target and real date
                    if article_date == self.date:
                        # If date is equal, then get article url
                        link = article.find("a", {"data-test": "article-title-link"})
                        if link and "href" in link.attrs:
                            # add article information to dict
                            self.data["urls"].append(link["href"])
                            self.data["articles"].append(
                                await self.fetch_article(session, link["href"])
                            )
                            self.data["date"].append(article_date)
                            self.data["time"].append(
                                time_element["datetime"].split(" ")[-1]
                            )

    async def parse(self):
        """Create async request session and execute parsing"""
        async with aiohttp.ClientSession() as session:
            await self.fetch_urls(session)
            return self.data
