import asyncio
from datetime import datetime
from src.parser.async_parser import AsyncParser
from src.agent.main import Agent, system_translate_eng_prompt
from src.bot.articles import Articles

agent = Agent()
articles = Articles()


async def save_to_json(data):
    existing_data = await articles.load_articles()

    # Добавляем новые статьи, если они ещё не существуют в файле
    for entry in reversed(data):
        url = entry["url"]
        if url not in existing_data:
            existing_data[url] = dict(article=entry["article"], date=entry["date"], time=entry["time"],
                                      summarization_article=await agent.summarization(entry["article"]),
                                      english_article=await agent.translation(entry["article"],
                                                                              system_translate_eng_prompt))
            print(url)
            await asyncio.sleep(3)

    # Записываем обновлённые данные в файл
    await articles.save_articles(existing_data)
    print("end parsing")


async def main(target_date: str) -> None:
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
        await save_to_json(data_to_save)
    else:
        print("No articles found or failed to fetch the page.")

if __name__ == "__main__":
    asyncio.run(main(datetime.today().strftime('%Y-%m-%d')))
