import os
from typing import Any
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
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

articles = Articles()
api_key = config("config.ini", "tokens")["api_token"]
os.environ["GOOGLE_API_KEY"] = api_key
database = Database()
parser = StrOutputParser()
system_agent_prompt = ("You are an AI assistant specifically designed to assist with queries related to cryptocurrency."
                       " Your primary task is to search for and retrieve information from the vector store,"
                       " which contains documents specifically related to cryptocurrency topics."
                       " If the user's query is related to cryptocurrency,"
                       " search the vector store for relevant information and provide a detailed response."
                       " If the user's query is not related to cryptocurrency,"
                       " kindly inform them that you can only assist with cryptocurrency-related questions."
                       " Always respond in a polite and professional manner."
                       " Your responses must not contain harmful, unethical, racist, sexist, toxic,"
                       " dangerous or illegal content."
                       " Please ensure that your responses are socially unbiased and positive in nature."
                       "Remember, you should only use the information stored"
                       " in the vector store to answer questions related to cryptocurrency."
                       " If you don't know the answer to a question, please don't spread false information.")

system_sum_prompt = ("Твоя задача написать краткое содержание новости по теме криптовалют."
                     "Напиши главный смысл новости используя 1 или 2 предложения.")
system_translate_rus_prompt = ("Твоя задача перевести данный текст на русский."
                               "Если текст уже на русском, то верни его в исходном состоянии."
                               "Если в тексте написан бред, то вежливо скажи, что не можешь ответить на запрос")
system_translate_eng_prompt = ("Your task is to translate this text into English."
                               "If text already in english, then just return origin text."
                               "Your response have to consist only translated text")

user_prompt = PromptTemplate.from_template("You must answer only to query is related to cryptocurrency."
                                           "Do it correctly and informatively."
                                           "This is my query: {query}")


class Agent:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Agent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.__model = ChatGoogleGenerativeAI(model="gemini-1.5-flash",
                                                  temperature=0.2,
                                                  top_p=0.5,
                                                  max_tokens=512)
            self.__system_message = SystemMessage(content=system_agent_prompt)
            self.__trimmer = trim_messages(
                max_tokens=500,
                strategy="last",
                token_counter=self.model,
                include_system=True,
                allow_partial=False,
                start_on="human",
            )
            self.__agent_executor = None
            self.__retriever_from_llm_chain = None
            self.__tool = None
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

    @property
    def retriever_from_llm_chain(self):
        return self.__retriever_from_llm_chain

    @property
    def tool(self):
        return self.__tool

    @staticmethod
    async def load_articles_as_documents():
        # Преобразование статей из `Articles` в формат документов, ожидаемый LangChain
        docs = []
        for url, content in articles.all_articles.items():
            docs.append(Document(page_content=content["english_article"], metadata={
                "url": url,
                "date": content["date"]
            }))
        return docs

    async def generate_agent_executor(self):
        docs = await self.load_articles_as_documents()

        # 2. Разбиение на части
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=750, chunk_overlap=500)
        splits = text_splitter.split_documents(docs)
        print(f"Number of splits: {len(splits)}")

        # 3. Векторизация
        try:
            vectorstore = Chroma.from_documents(documents=splits,
                                                embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"))
        except Exception as e:
            print(f"Error during vectorization: {e}")
            raise

        # 4. Настройка ретривера
        retriever = vectorstore.as_retriever()

        # 5. Настройка RePhraseQueryRetriever с LLMChain
        query_prompt = PromptTemplate(
            input_variables=["question"],
            template="""You are an assistant tasked with taking a natural language query from a user
            and converting it into a query for a vectorstore. In the process, strip out all 
            information that is not relevant for the retrieval task and return a new, simplified
            question for vectorstore retrieval. Here is the user query: {question}""",
        )

        llm = self.model
        llm_chain = LLMChain(llm=llm, prompt=query_prompt)

        self.__retriever_from_llm_chain = RePhraseQueryRetriever(
            retriever=retriever,
            llm_chain=llm_chain
        )

        # 6. Настройка инструмента с RePhraseQueryRetriever
        self.__tool = create_retriever_tool(
            self.__retriever_from_llm_chain,
            "article_retriever",
            "Searches and returns excerpts from the articles about cryptocurrencies."
            "Try to returns all relative information"
        )
        tools = [self.tool]

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

    async def translation(self, text: str, sys_prompt) -> str:
        chain = self.model | parser
        response = chain.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=text)
        ])
        return response

    async def answer(self, message: types.Message) -> types.Message:
        # Получаем историю сообщений пользователя
        history = await database.get_user_history(message.from_user.id)

        # Добавляем текущий запрос пользователя
        eng_query = await self.translation(message.text, system_translate_eng_prompt)
        history.append(HumanMessage(content=user_prompt.format(query=eng_query)))

        chain = self.model | parser
        response = ""
        initial_response = "⏳ Ищем информацию..."
        generate_response = "⏳ Генерация ответа..."
        loading_symbols = ["⏳", "⌛"]
        loading_index = 0
        flag = True

        answer_message = await message.answer(initial_response)
        rag_response = self.agent_executor.invoke({"messages": await self.formatted_history(history)})
        await answer_message.edit_text(generate_response)
        async for event in chain.astream_events([
            SystemMessage(content=system_translate_rus_prompt),
            HumanMessage(content=rag_response["messages"][-1].content)
        ], version="v1"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    response += content
                    if flag:
                        flag = False
                    else:
                        try:
                            await answer_message.edit_text(response)
                        except Exception:
                            pass
            elif kind == "on_chain_start":
                await answer_message.edit_text(f"{generate_response} {loading_symbols[loading_index]}")
                loading_index = (loading_index + 1) % len(loading_symbols)

        # Обновляем окончательный ответ
        try:
            await answer_message.edit_text(response)
        except Exception:
            pass
        # Добавляем ответ в историю
        history.append(AIMessage(content=rag_response["messages"][-1].content))
        trimmed_history = self.trimmer.invoke(history)
        # Обновляем историю пользователя в базе данных
        await database.update_user_history(message.from_user.id, trimmed_history)
        print("successfully answer to query!")
        return answer_message

    async def test_greeting(self, query: str) -> str:
        history = await database.get_user_history(1044539451)

        # Добавляем текущий запрос пользователя
        eng_query = await self.translation(query, system_translate_eng_prompt)
        history.append(HumanMessage(content=user_prompt.format(query=eng_query)))

        # Преобразуем историю в правильный формат для agent_executor
        formatted_history = await self.formatted_history(history)
        response = self.agent_executor.invoke({"messages": formatted_history})
        print(response)
        final_response = await self.translation(response["messages"][-1].content, system_translate_rus_prompt)
        return final_response

    async def test_query(self, query: str) -> str:
        eng_query = await self.translation(query, system_translate_eng_prompt)
        print(f"Original query: {eng_query}")

        # Получение модифицированного запроса
        modified_query = self.retriever_from_llm_chain.llm_chain.run({"question": user_prompt.format(query=eng_query)})

        # Вывод модифицированного запроса
        print(f"Modified query: {modified_query}")

        assert eng_query != modified_query

        return modified_query

    async def test_tool(self, query: str) -> str:
        tool_result = self.tool.run(query)

        print(f"Tool result: {tool_result}")

        return tool_result
