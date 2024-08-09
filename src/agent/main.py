from aiogram import types
from config.config import config
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage
from src.pgsqldatabase.database import Database
from langchain_core.messages import SystemMessage, trim_messages, AIMessage
from langchain_core.output_parsers import StrOutputParser

api_key = config("config.ini", "tokens")["api_token"]
database = Database()
parser = StrOutputParser()
system_agent_prompt = ("Веди себя как чат-бот."
                       "При создании контента придерживайтесь следующих правил тона и стиля:"
                       "Используйте дружелюбный, разговорный тон, который легко понять."
                       "Пиши коротко и только нужную информацию."
                       "Избегайте жаргона и технических терминов без крайней необходимости."
                       "Убедись, что весь контент грамматически правильный и не содержит орфографических ошибок."
                       "Не используй случайные символы."
                       "Отвечай только на русском языке! Не используй токены на других языках.")

system_sum_prompt = ("Твоя задача написать краткое содержание новости по теме криптовалют."
                     "Напиши главный смысл новости используя 1 или 2 предложения.")


class Agent:
    def __init__(self):
        self.__model = ChatNVIDIA(model="meta/llama-3.1-405b-instruct",
                                  api_key=api_key,
                                  temperature=0.2,
                                  top_p=0.7,
                                  max_tokens=256)
        self.__system_message = SystemMessage(
            content=system_agent_prompt)
        self.__trimmer = trim_messages(
            max_tokens=3000,
            strategy="last",
            token_counter=self.model,
            include_system=True,
            allow_partial=False,
            start_on="human",
        )

    @property
    def model(self):
        return self.__model

    @property
    def system_message(self):
        return self.__system_message

    @property
    def trimmer(self):
        return self.__trimmer

    async def summarization(self, text: str) -> str:
        chain = self.model | parser
        response = chain.invoke([
            SystemMessage(content=system_sum_prompt),
            HumanMessage(content=text)
        ])
        return response

    async def test_greeting(self, query: str) -> str:
        chain = self.model | parser
        response = chain.invoke([
            SystemMessage(content=system_agent_prompt),
            HumanMessage(content=query)
        ])
        return response

    async def answer(self, message: types.Message) -> types.Message:
        # Получаем историю сообщений пользователя
        history = await database.get_user_history(message.from_user.id)
        if not history:
            history.append(self.system_message)

        # Добавляем текущий запрос пользователя
        history.append(HumanMessage(content=f"Пожалуйста, отвечай на этот запрос исключительно на русском языке:"
                                            f" {message.text}"))

        trimmed_history = self.trimmer.invoke([self.system_message] + history)

        # Создаем цепочку и получаем ответ
        chain = self.model | parser
        response = ""
        token_count = 0
        initial_response = "⏳ Генерация ответа..."
        loading_symbols = ["⏳", "⌛"]
        loading_index = 0
        flag = True

        answer_message = await message.answer(initial_response)

        async for event in chain.astream_events(trimmed_history, version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    response += content
                    token_count += 1
                    if token_count % 20 == 0:
                        if flag:
                            flag = False
                        else:
                            await answer_message.edit_text(response)
            elif kind == "on_chain_start":
                await answer_message.edit_text(f"{initial_response} {loading_symbols[loading_index]}")
                loading_index = (loading_index + 1) % len(loading_symbols)

        # Обновляем окончательный ответ
        await answer_message.edit_text(response)
        # Добавляем ответ в историю
        trimmed_history.append(AIMessage(content=response))

        # Обновляем историю пользователя в базе данных
        await database.update_user_history(message.from_user.id, trimmed_history)
        return answer_message
