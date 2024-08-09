import asyncio
import json
from datetime import datetime
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
    for entry in data:
        url = entry["url"]
        if url not in existing_data:
            existing_data[url] = dict(article=entry["article"], date=entry["date"],
                                      summarization_article=await agent.summarization(entry["article"]))

    # Записываем обновлённые данные в файл
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=4)


async def main():
    target_date = datetime.today().strftime('%Y-%m-%d')
    parser = AsyncParser(target_date)
    articles = await parser.parse()

    # Формируем структуру для сохранения в JSON
    data_to_save = [{"url": url, "article": article,
                     "date": target_date} for url, article in zip(parser.urls, articles)]

    if data_to_save:
        await save_to_json(data_to_save, 'articles.json')
    else:
        print("No articles found or failed to fetch the page.")


if __name__ == '__main__':
    asyncio.run(main())
