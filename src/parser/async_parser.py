from bs4 import BeautifulSoup
import aiohttp
import asyncio

URL = "https://ru.investing.com/news/cryptocurrency-news"


class AsyncParser:
    def __init__(self, date):
        self.__date = date
        self.__urls = []

    @property
    def date(self):
        return self.__date

    @property
    def urls(self):
        return self.__urls

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
        async with session.get(URL) as response:
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
                            # Добавляем ссылку в список
                            self.urls.append(link["href"])

        return self.urls

    async def parse(self):
        async with aiohttp.ClientSession() as session:
            await self.fetch_urls(session)
            tasks = [self.fetch_article(session, url) for url in self.urls]
            articles = await asyncio.gather(*tasks)
            return articles