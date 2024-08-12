import json
import os
from src.parser.async_parser import AsyncParser
from src.agent.main import Agent

agent = Agent()


async def load_existing_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


async def save_to_json(data, filename):
    existing_data = await load_existing_data(filename)

    # Добавляем новые статьи, если они ещё не существуют в файле
    for entry in reversed(data):
        url = entry["url"]
        if url not in existing_data:
            existing_data[url] = dict(article=entry["article"], date=entry["date"], time=entry["time"],
                                      summarization_article=await agent.summarization(entry["article"]))
            print(url)

    # Записываем обновлённые данные в файл
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)


async def main(target_date: str) -> None:
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
        await save_to_json(data_to_save, 'articles.json')
    else:
        print("No articles found or failed to fetch the page.")
