"""
A module for encode and decode json formate

There are an inherit class from json.JSONEncoder to encode json formate and decode function
to decode json file. This module use only in Database class to update and get row history.
Typical usage example:

    from src.pgsqldatabase.json_encoder import message_decoder, MessageEncoder

    json.loads(row[4], object_hook=message_decoder)
    json.dumps(new_history, cls=MessageEncoder)
"""

import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class MessageEncoder(json.JSONEncoder):
    """Encode langchain type message to json format"""

    def default(self, message: SystemMessage | HumanMessage | AIMessage | dict) -> dict:
        """Encode message to json formate to write it to database

        Attributes:
            message: one of langchain_core.messages

        Returns:
            dict with keys "_type" ("HumanMessage" - user query or "AIMessage" - LLM response) and
            "content" (message text)
        """
        if (
            isinstance(message, SystemMessage)
            or isinstance(message, HumanMessage)
            or isinstance(message, AIMessage)
        ):
            return {"_type": message.__class__.__name__, "content": message.content}
        return super().default(message)


def message_decoder(json_dict: dict) -> SystemMessage | HumanMessage | AIMessage | dict:
    """Decorate json format to langchain type message

    Attributes:
        json_dict: json format dict with keys "_type" ("HumanMessage" - user query or "AIMessage" - LLM response) and
        "content" (message text)

    Returns:
        one of langchain_core.messages
    """
    if "_type" in json_dict:
        msg_type = json_dict["_type"]
        content = json_dict["content"]
        if msg_type == "SystemMessage":
            return SystemMessage(content=content)
        elif msg_type == "HumanMessage":
            return HumanMessage(content=content)
        elif msg_type == "AIMessage":
            return AIMessage(content=content)
    return json_dict
