from config.config import config
import openai


system_content = "Express yourself like a Billy Harrington. Speaking only in russian."

client = openai.OpenAI(
    api_key=config("config.ini", "tokens")["openai_token"],
    base_url="https://api.aimlapi.com",
)


def answer(query: str) -> str:
    chat_completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": query},
        ],
        temperature=0.7,
        max_tokens=128,
    )
    response = chat_completion.choices[0].message.content
    return response
