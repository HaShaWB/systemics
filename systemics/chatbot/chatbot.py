# chatbot/chatbot.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..languageModel.LM import LM

from .chatObj import *
from .chatbotError import *

class Chatbot:
    """
    Chatbot class for managing chat interactions and language model responses
    """

    def __init__(self, lm: LM):
        """
        Initialize the Chatbot

        :param lm: Language model instance
        """
        self.lm = lm
        self.chat_history: list[ChatObj] = []
        self.total_used_tokens: dict[str, int] = {
            "completion_tokens" : 0,
            "prompt_tokens" : 0,
            "total_tokens" : 0
        }

    def set_chat(self, chat: ChatObj, index: int):
        """
        Set a chat object at a specific index in the chat history

        :param chat: ChatObj to set
        :param index: Index to set the chat object at
        """
        self.chat_history[index] = chat

    def insert_chat(self, chat: ChatObj, index: int):
        """
        Insert a chat object at a specific index in the chat history

        :param chat: ChatObj to insert
        :param index: Index to insert the chat object at (-1 for append)
        """
        if index == -1:
            self.chat_history.append(chat)
        else:
            self.chat_history.insert(index, chat)

    def add_chat(self, chat: ChatObj):
        """
        Add a chat object to the end of the chat history

        :param chat: ChatObj to add
        """
        self.chat_history.insert(chat, -1)

    def remove_chat(self, index = -1):
        """
        Remove a chat object from the chat history

        :param index: Index of the chat object to remove (-1 for last)
        """
        if index == -1:
            self.chat_history.pop()
        else:
            self.chat_history.pop(index)
            
    
    def generate_response(self, add_to_history: bool = True,
                          temperature: float = 1, 
                          top_p: float = 1, 
                          max_tokens: int | None = None, **kwargs) -> ChatObj:
        """
        Generate a response using the language model

        :param add_to_history: Whether to add the response to chat history
        :param temperature: Temperature for response generation
        :param top_p: Top p value for response generation
        :param max_tokens: Maximum number of tokens for the response
        :param kwargs: Additional keyword arguments for the language model
        :return: Generated AssistantChat object
        """
        messages = chatObjs_to_list(self.chat_history)
        response, usage = self.lm.generate_chat(messages, temperature, top_p, max_tokens, **kwargs)

        self.total_used_tokens["completion_tokens"] += usage["completion_tokens"]
        self.total_used_tokens["prompt_tokens"] += usage["prompt_tokens"]
        self.total_used_tokens["total_tokens"] += usage["total_tokens"]

        if add_to_history:
            self.add_chat(AssistantChat(response))

        return AssistantChat(response)
    
