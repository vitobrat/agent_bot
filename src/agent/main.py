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


class Agent:
    def __init__(self):
        self.__model = ChatNVIDIA(model="meta/llama-3.1-405b-instruct")
        self.__system_message = SystemMessage(
            content="Express yourself like a chat bot. Answering only in russian language")
        self.__trimmer = trim_messages(
            max_tokens=5000,
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

    async def answer(self, message: types.Message) -> str:
        # Получаем историю сообщений пользователя
        history = await database.get_user_history(message.from_user.id)
        if not history:
            history.append(self.system_message)

        # Добавляем текущий запрос пользователя
        history.append(HumanMessage(content=message.text))

        trimmed_history = self.trimmer.invoke([self.system_message] + history)
        print(trimmed_history)

        # Создаем цепочку и получаем ответ
        chain = self.model | parser
        response = chain.invoke(trimmed_history)

        # Добавляем ответ в историю
        trimmed_history.append(AIMessage(content=response))

        # Обновляем историю пользователя в базе данных
        await database.update_user_history(message.from_user.id, trimmed_history)

        return response

