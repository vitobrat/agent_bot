import os
from typing import List, Dict, Any

from aiogram import types
from config.config import config
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from src.pgsqldatabase.database import Database
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import SystemMessage, trim_messages, AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from src.bot.articles import Articles
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.schema import Document
from langchain.retrievers import RePhraseQueryRetriever
from langchain.chains import LLMChain

articles = Articles()
api_key = config("config.ini", "tokens")["api_token"]
os.environ["NVIDIA_API_KEY"] = api_key
database = Database()
parser = StrOutputParser()
system_agent_prompt = ("Express yourself like a chatbot")

system_sum_prompt = ("Твоя задача написать краткое содержание новости по теме криптовалют."
                     "Напиши главный смысл новости используя 1 или 2 предложения.")
system_translate_prompt = ("Твоя задача перевести данный текст на русский."
                           "Если текст уже на русском, то верни его в исходном состоянии."
                           "Если в тексте написан бред, то вежливо скажи, что не можешь ответить на запрос")
user_prompt = PromptTemplate.from_template("You must answer correctly, briefly and informatively."
                                           "This is my query: {query}")


class Agent:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Agent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Чтобы избежать повторной инициализации
            self.__model = ChatNVIDIA(model="meta/llama-3.1-405b-instruct",
                                      temperature=0.1,
                                      top_p=0.7,
                                      max_tokens=256)
            self.__system_message = SystemMessage(content=system_agent_prompt)
            self.__trimmer = trim_messages(
                max_tokens=1000,
                strategy="last",
                token_counter=self.model,
                include_system=True,
                allow_partial=False,
                start_on="human",
            )
            self.__agent_executor = None
            self._initialized = True

    @property
    def model(self):
        return self.__model

    @property
    def system_message(self):
        return self.__system_message

    @property
    def trimmer(self):
        return self.__trimmer

    @property
    def agent_executor(self):
        return self.__agent_executor

    @staticmethod
    async def load_articles_as_documents():
        # Преобразование статей из `Articles` в формат документов, ожидаемый LangChain
        docs = []
        for url, content in articles.all_articles.items():
            docs.append(Document(page_content=content["article"], metadata={"url": url}))
        return docs

    async def generate_agent_executor(self):
        docs = await self.load_articles_as_documents()

        # 2. Разбиение на части
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=100)
        splits = text_splitter.split_documents(docs)
        print(f"Number of splits: {len(splits)}")

        # 3. Векторизация
        try:
            vectorstore = Chroma.from_documents(documents=splits, embedding=NVIDIAEmbeddings())
        except Exception as e:
            print(f"Error during vectorization: {e}")
            raise

        # 4. Настройка ретривера
        retriever = vectorstore.as_retriever()

        # 5. Настройка RePhraseQueryRetriever с LLMChain
        QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an assistant tasked with taking a natural language query from a user
            and converting it into a query for a vectorstore. In the process, strip out all 
            information that is not relevant for the retrieval task and return a new, simplified
            question for vectorstore retrieval. Here is the user query: {question}""",
        )

        llm = self.model
        llm_chain = LLMChain(llm=llm, prompt=QUERY_PROMPT)

        retriever_from_llm_chain = RePhraseQueryRetriever(
            retriever=retriever,
            llm_chain=llm_chain
        )

        # 6. Настройка инструмента с RePhraseQueryRetriever
        tool = create_retriever_tool(
            retriever_from_llm_chain,
            "article_retriever",
            "Searches and returns excerpts from the articles."
        )
        tools = [tool]

        # 7. Настройка REACT агента
        self.__agent_executor = create_react_agent(self.model, tools)

    async def summarization(self, text: str) -> str:
        chain = self.model | parser
        response = chain.invoke([
            SystemMessage(content=system_sum_prompt),
            HumanMessage(content=text)
        ])
        return response

    @staticmethod
    async def formatted_history(history: list) -> list[dict[str, str] | Any]:
        return [
            {"role": "system", "content": system_agent_prompt},
            *[
                {"role": "user" if isinstance(msg, HumanMessage) else "assistant", "content": msg.content}
                for msg in history
            ]
        ]

    async def test_greeting(self, query: str) -> str:
        history = await database.get_user_history(1044539451)
        if not history:
            history.append(self.system_message)

        # Добавляем текущий запрос пользователя
        history.append(HumanMessage(content=user_prompt.format(query=query)))

        trimmed_history = self.trimmer.invoke(history)

        # Преобразуем историю в правильный формат для agent_executor
        formatted_history = await self.formatted_history(trimmed_history)
        print(formatted_history)
        response = self.agent_executor.invoke({"messages": formatted_history})
        print(response)
        chain = self.model | parser
        final_response = chain.invoke([
            SystemMessage(content=system_translate_prompt),
            HumanMessage(content=response["messages"][-1].content)
        ])
        return final_response

    async def answer(self, message: types.Message) -> types.Message:
        # Получаем историю сообщений пользователя
        history = await database.get_user_history(message.from_user.id)
        if not history:
            history.append(self.system_message)

        # Добавляем текущий запрос пользователя
        history.append(HumanMessage(content=user_prompt.format(query=message.text)))

        trimmed_history = self.trimmer.invoke(history)

        chain = self.model | parser
        response = ""
        token_count = 0
        initial_response = "⏳ Ищем информацию..."
        generate_response = "⏳ Генерация ответа..."
        loading_symbols = ["⏳", "⌛"]
        loading_index = 0
        flag = True

        answer_message = await message.answer(initial_response)
        rag_response = self.agent_executor.invoke({"messages": await self.formatted_history(trimmed_history)})
        await answer_message.edit_text(generate_response)
        print(rag_response["messages"][-1].content)
        async for event in chain.astream_events([
            SystemMessage(content=system_translate_prompt),
            HumanMessage(content=rag_response["messages"][-1].content)
        ], version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    response += content
                    token_count += 1
                    if token_count % 10 == 0:
                        if flag:
                            flag = False
                        else:
                            await answer_message.edit_text(response)
            elif kind == "on_chain_start":
                await answer_message.edit_text(f"{generate_response} {loading_symbols[loading_index]}")
                loading_index = (loading_index + 1) % len(loading_symbols)

        # Обновляем окончательный ответ
        await answer_message.edit_text(response)
        # Добавляем ответ в историю
        trimmed_history.append(AIMessage(content=response))

        # Обновляем историю пользователя в базе данных
        await database.update_user_history(message.from_user.id, trimmed_history)
        return answer_message
