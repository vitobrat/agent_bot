import os
from aiogram import types
from config.config import config
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from src.pgsqldatabase.database import Database
from langchain_core.messages import SystemMessage, trim_messages, AIMessage
from langchain_core.output_parsers import StrOutputParser

os.environ["NVIDIA_API_KEY"] = config("config.ini", "tokens")["api_token"]
database = Database()
parser = StrOutputParser()
system_prompt = ("Express yourself like a chatbot."
                 "When generating content, adhere to the following tone and style guidelines:"
                 "Use a friendly, conversational tone that is easy to understand."
                 "Write in short, concise sentences and paragraphs."
                 "Use active voice whenever possible."
                 "Avoid jargon or technical terms unless absolutely necessary."
                 "Use bullet points or numbered lists to break up long passages and improve readability."
                 "Ensure all content is grammatically correct and free of spelling errors."
                 "Do not use strange symbols."
                 "Express yourself ONLY in russian language! Do not input tokens from another language.")


class Agent:
    def __init__(self):
        self.__model = ChatNVIDIA(model="meta/llama-3.1-405b-instruct")
        self.__system_message = SystemMessage(
            content=system_prompt)
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

    async def answer(self, message: types.Message) -> types.Message:
        # Получаем историю сообщений пользователя
        history = await database.get_user_history(message.from_user.id)
        if not history:
            history.append(self.system_message)

        # Добавляем текущий запрос пользователя
        history.append(HumanMessage(content=message.text))

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
