import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


class MessageEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SystemMessage) or isinstance(o, HumanMessage) or isinstance(o, AIMessage):
            return {
                '_type': o.__class__.__name__,
                'content': o.content
            }
        return super().default(o)


def message_decoder(d):
    if '_type' in d:
        msg_type = d['_type']
        content = d['content']
        if msg_type == 'SystemMessage':
            return SystemMessage(content=content)
        elif msg_type == 'HumanMessage':
            return HumanMessage(content=content)
        elif msg_type == 'AIMessage':
            return AIMessage(content=content)
    return d
