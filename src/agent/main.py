import os
from config.config import config
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

os.environ["NVIDIA_API_KEY"] = config("config.ini", "tokens")["openai_token"]


model = ChatNVIDIA(model="meta/llama3-70b-instruct")
parser = StrOutputParser()
system_message = SystemMessage(content="Express yourself like a chat bot. Answering only in russian language")


def answer(query: str) -> str:
    messages = [
        system_message,
        HumanMessage(content=query),
    ]
    chain = model | parser
    return chain.invoke(messages)



