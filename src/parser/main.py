"""
This a method parse articles and save it

This method occur parsing data by AsyncParser class and form it in dict
(article url, article text, article date, article time, article summarization information, article text in english)
and save it in articles.json
Only new articles are added in each call, articles whose url is already accounted for in dict are missing
Typical usage example:

    from src.parser.main import main as parser_main

    asyncio.create_task(parser_main(target_time))
"""
import asyncio
from datetime import datetime
from src.parser.async_parser import AsyncParser
from src.agent.main import Agent
from src.agent.prompts import SYSTEM_TRANSLATE_ENG_PROMPT
from src.articles.articles import Articles


async def save_to_json(data: list[dict], agent: Agent, articles: Articles):
    existing_data = await articles.load_articles()

    # Добавляем новые статьи, если они ещё не существуют в файле
    for entry in reversed(data):
        url = entry["url"]
        if url not in existing_data:
            existing_data[url] = dict(article=entry["article"], date=entry["date"], time=entry["time"],
                                      summarization_article=await agent.summarization(entry["article"]),
                                      english_article=await agent.translation(entry["article"],
                                                                              SYSTEM_TRANSLATE_ENG_PROMPT))
            print(url)
            await asyncio.sleep(3)

    # Записываем обновлённые данные в файл
    await articles.save_articles(existing_data)
    print("end parsing")


async def main(target_date=datetime.today().strftime('%Y-%m-%d')) -> None:
    agent = Agent()
    articles = Articles()
    print("start parsing")
    target_date = target_date
    parser = AsyncParser(target_date)
    await parser.parse()

    # Формируем структуру для сохранения в JSON
    data_to_save = [{"url": url, "article": article,
                     "date": date, "time": time} for url, article, date, time in zip(parser.data["urls"],
                                                                                     parser.data["articles"],
                                                                                     parser.data["date"],
                                                                                     parser.data["time"])]

    if data_to_save:
        await save_to_json(data_to_save, agent, articles)
    else:
        print("No articles found or failed to fetch the page.")


if __name__ == "__main__":
    asyncio.run(main(datetime.today().strftime('%Y-%m-%d')))
