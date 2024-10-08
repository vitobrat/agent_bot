"""
This module implement RAG agent chatbot

This module creates a model that runs in LLM (currently on gemini-1.5-flash).
It connects via an api key. Then it creates extraction vectors from the article text and makes a retriever tool
that finds the information in the retriever. After that from the model and the retriever tool it creates a RAG agent.
The database stores the history of each user, so when the user makes a query,
the RAG agent starts building the response:
The response is constructed from the vector text fragments that the retriever tool returns to the user's query,
user request, and the context of the conversation history from the database.
The model analyses all these components and responds.
The model configuration only answers queries about cryptocurrencies.
The model mainly uses information from articles, but if the query does not match information from the vector store,
then the model builds a response based on its own knowledge base,
but taking into account the context of cryptocurrencies.
Typical usage example:

    from src.agent.main import Agent

    agent = Agent()
    await agent.generate_agent_executor()
"""

import os
from typing import Any
from aiogram import types
from config.config import config
from langchain_core.messages import (
    SystemMessage,
    trim_messages,
    AIMessage,
    HumanMessage,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain.schema import Document
from langchain.retrievers import RePhraseQueryRetriever
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.pgsqldatabase.database import Database
from src.articles.articles import Articles
from src.agent.prompts import (
    USER_PROMPT,
    SYSTEM_AGENT_PROMPT,
    SYSTEM_SUM_PROMPT,
    TOOL_DESCRIPTION,
    SYSTEM_TRANSLATE_ENG_PROMPT,
    SYSTEM_TRANSLATE_RUS_PROMPT,
    QUERY_PROMPT,
    GENERATE_RESPONSE,
    INITIAL_RESPONSE,
    loading_symbols,
)

api_key = config("config.ini", "tokens")["api_token"]
os.environ["GOOGLE_API_KEY"] = api_key


class Agent:
    """Singleton class that realize RAG agent"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Agent, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initial configurate attributes"""
        if not hasattr(self, "_initialized"):
            self.__model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash", temperature=0.2, top_p=0.5, max_tokens=512
            )
            self.__system_message = SystemMessage(content=SYSTEM_AGENT_PROMPT)
            self.__trimmer = trim_messages(
                max_tokens=2000,
                strategy="last",
                token_counter=self.model,
                include_system=True,
                allow_partial=False,
                start_on="human",
            )
            self.__agent_executor = None
            self.__retriever_from_llm_chain = None
            self.__tool = None
            self.__parser = StrOutputParser()
            self._initialized = True

    @property
    def model(self):
        return self.__model

    @property
    def parser(self):
        return self.__parser

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
    async def load_articles_as_documents() -> list[Document]:
        """Transformation articles from "Articles" in format waiting LangChain

        Returns:
            list of Documents which further separates to chain and add to vector store
        """
        articles = Articles()
        docs = []
        for url, content in articles.all_articles.items():
            docs.append(
                Document(
                    page_content=content["english_article"],
                    metadata={"url": url, "date": content["date"]},
                )
            )
        return docs

    async def generate_agent_executor(self) -> None:
        """Initial RAG agent"""
        # 1. Transform articles to list of "Document"
        docs = await self.load_articles_as_documents()

        # 2. Separate to chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=750, chunk_overlap=500
        )
        splits = text_splitter.split_documents(docs)
        print(f"Number of splits: {len(splits)}")

        # 3. Vectorize
        try:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            )
        except Exception as e:
            print(f"Error during vectorization: {e}")
            raise

        # 4. Retriever configurate
        retriever = vectorstore.as_retriever()

        # 5. Configurate RePhraseQueryRetriever with LLMChain.
        # It changes user query specifically for searching in vector store
        query_prompt = PromptTemplate(
            input_variables=["question"],
            template=QUERY_PROMPT,
        )

        llm = self.model
        llm_chain = LLMChain(llm=llm, prompt=query_prompt)

        self.__retriever_from_llm_chain = RePhraseQueryRetriever(
            retriever=retriever, llm_chain=llm_chain
        )

        # 6. Configurate tool with RePhraseQueryRetriever
        # It output most relevant chunks to user query
        self.__tool = create_retriever_tool(
            self.__retriever_from_llm_chain, "article_retriever", TOOL_DESCRIPTION
        )
        tools = [self.tool]

        # 7. Configurate RAG agent
        self.__agent_executor = create_react_agent(self.model, tools)

    async def summarization(self, text: str) -> str:
        """Summarize text in 2-3 sentences

        Attributes:
            text: string is needed to summarize

        Returns:
            summarize text
        """
        chain = self.model | self.parser
        response = chain.invoke(
            [SystemMessage(content=SYSTEM_SUM_PROMPT), HumanMessage(content=text)]
        )
        print(response)
        return response

    @staticmethod
    async def formatted_history(history: list) -> list[dict[str, str] | Any]:
        """Transform LangChain Messages to input type for agent

        Attributes:
            history: list of SystemMessage or AIMessage or HumanMessage

        Returns:
            list of dicts that can be written by RAG agent
        """
        return [
            {"role": "system", "content": SYSTEM_AGENT_PROMPT},
            *[
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content,
                }
                for msg in history
            ],
        ]

    async def translation(self, text: str, sys_prompt: str) -> str:
        """Translate text to another language

        Translate text from english to russian or russian to english

        Attributes:
            text: text that needs to translate
            sys_prompt: prompt (SYSTEM_TRANSLATE_ENG_PROMPT translate to english
            or SYSTEM_TRANSLATE_RUS_PROMPT translate to russian)
        """
        chain = self.model | self.parser
        response = chain.invoke(
            [SystemMessage(content=sys_prompt), HumanMessage(content=text)]
        )
        return response

    async def answer(self, message: types.Message) -> types.Message:
        """RAG agent response to user query

        Attributes:
            message: telegram message that consist user query

        Returns:
             telegram message that consist model response
        """
        database = Database()
        # Get user dialog history
        history = await database.get_user_history(message.from_user.id)

        # Add to history current user query
        eng_query = await self.translation(message.text, SYSTEM_TRANSLATE_ENG_PROMPT)
        history.append(HumanMessage(content=USER_PROMPT.format(query=eng_query)))

        chain = self.model | self.parser
        response = ""
        loading_index = 0
        flag = True

        answer_message = await message.answer(INITIAL_RESPONSE)

        # Transform dialog history to special format to agent executor
        rag_response = self.agent_executor.invoke(
            {"messages": await self.formatted_history(history)}
        )
        await answer_message.edit_text(GENERATE_RESPONSE)

        # stream model response
        async for event in chain.astream_events(
            [
                SystemMessage(content=SYSTEM_TRANSLATE_RUS_PROMPT),
                HumanMessage(content=rag_response["messages"][-1].content),
            ],
            version="v1",
        ):
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
                await answer_message.edit_text(
                    f"{GENERATE_RESPONSE} {loading_symbols[loading_index]}"
                )
                loading_index = (loading_index + 1) % len(loading_symbols)

        # Refresh message by last model response
        try:
            await answer_message.edit_text(response)
        except Exception:
            pass
        print(response)
        # Add model response to history
        history.append(AIMessage(content=rag_response["messages"][-1].content))
        trimmed_history = self.trimmer.invoke(history)
        # Update user dialog history in database
        await database.update_user_history(message.from_user.id, trimmed_history)
        print("successfully answer to query!")
        return answer_message

    async def test_greeting(self, query: str) -> str:
        """Test function to check model response

        Attributes:
            query: simulite user query

        Returns:
             model response
        """
        database = Database()
        history = await database.get_user_history(await database.get_all_admins_id()[0])

        eng_query = await self.translation(query, SYSTEM_TRANSLATE_ENG_PROMPT)
        history.append(HumanMessage(content=USER_PROMPT.format(query=eng_query)))

        formatted_history = await self.formatted_history(history)
        response = self.agent_executor.invoke({"messages": formatted_history})
        print(response)
        final_response = await self.translation(
            response["messages"][-1].content, SYSTEM_TRANSLATE_RUS_PROMPT
        )
        return final_response

    async def test_query(self, query: str) -> str:
        """Test how RePhraseQueryRetriever transform user query to vector store

        Attributes:
            query: user query

        Returns:
            transform user query
        """
        eng_query = await self.translation(query, SYSTEM_TRANSLATE_ENG_PROMPT)
        print(f"Original query: {eng_query}")

        # Получение модифицированного запроса
        modified_query = self.retriever_from_llm_chain.llm_chain.run(
            {"question": USER_PROMPT.format(query=eng_query)}
        )

        # Вывод модифицированного запроса
        print(f"Modified query: {modified_query}")

        return modified_query

    async def test_tool(self, query: str) -> str:
        """Test what create_retriever_tool output

        Attributes:
            query: user query

        Returns:
            Most relevant chunks to user query
        """
        tool_result = self.tool.run(query)
        print(f"Tool result: {tool_result}")
        return tool_result
