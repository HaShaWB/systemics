# chatbot/chatObj.py

import json

from .utils import list_to_str, dict_to_str
from .chatbot_error import ChatbotInputError

class ChatObj:
    """
    basic structure of chat object (OpenAI protocol)

    - role : role of the chat object
    - content : content of the chat object
    """
    def __init__(self, role: str, content: str):
        """
        basic structure of chat object (OpenAI protocol)

        :param role: "system" | "user" | "assistant"
        :param content: str
        """
        self.role = role
        self.content = content


    def json(self):
        """
        return chatObj in json format => {"role": str, "content": str}
        * OPENAI protocol : use this format for input

        :return: chatObj in json format
        """
        return json.dumps({"role": self.role, "content": self.content})
    

    def chat(self):
        """
        return chatObj in dict format => {"role": str, "content": str}
        * OPENAI protocol : use this format for input

        :return: chatObj in dict format
        """
        return {"role": self.role, "content": self.content}
    
    
    def __str__(self):
        return f"{self.role} : {self.content}"
    

class SystemChat(ChatObj):
    """
    basic structure of system chat object

    - content : content of the chat object
    """
    
    def __init__(self, content: str):
        """
        basic structure of system chat object

        :param content: str
        """
        super().__init__("system", content)


class UserChat(ChatObj):
    """
    basic structure of user chat object

    - content : content of the chat object
    """

    def __init__(self, content: str):
        """
        basic structure of user chat object

        :param content: str
        """
        super().__init__("user", content)


class AssistantChat(ChatObj):
    """
    basic structure of assistant chat object

    - content : content of the chat object
    """
    
    def __init__(self, content: str):
        """
        basic structure of assistant chat object

        :param content: str
        """
        super().__init__("assistant", content)


class AdvancedSystemChat(SystemChat):
    """
    basic structure of advanced system chat object

    - initial_content : plain content of the chat object (Intro of the LM prompt) 
        -> highly recommended to start with "you are a/an {major_role}" (for example, "you are a helpful assistant")
    - generating_rules : generating rules of the chat object (optional, highly recommended)
    - assistant_profile : assistant profile of the chat object (optional)   
    - user_profile : user profile of the chat object (optional)
    """

    def __init__(self, initial_content: str = "you are a helpful assistant",
                 generating_rules: list[str]|str|None = None, 
                 assistant_profile: dict|str|None = None, 
                 user_profile: dict|str|None = None):
        """
        advanced structure of advanced system chat object with specific instructions

        :param content: str
        :param generating_rules: list[str]|str|None = None
        :param assistant_profile: dict|str|None = None
        :param user_profile: dict|str|None = None
        """
        
        self.initial_content = initial_content
        self.generating_rules = generating_rules
        self.assistant_profile = assistant_profile
        self.user_profile = user_profile

        initial_content = self.construct_content()
        super().__init__(initial_content)

    
    def construct_content(self, use_generating_rules: bool = True, 
                          use_assistant_profile: bool = True, 
                          use_user_profile: bool = True):
        """
        construct content of the advanced system chat object

        :param use_generating_rules: whether to use generating rules
        :param use_assistant_profile: whether to use assistant profile
        :param use_user_profile: whether to use user profile
        
        :return: content of the advanced system chat object
        """
        
        content = self.initial_content

        if use_generating_rules and self.generating_rules is not None:
            if type(self.generating_rules) == str:
                content = content + "\n\n### generating rules: \n" + self.generating_rules
            elif type(self.generating_rules) == list:
                content = content + "\n\n### generating rules: \n" + list_to_str(self.generating_rules, bullet = "\t - ")
            else: 
                raise ChatbotInputError("generating_rules must be a string or a list of strings")
            
        if use_assistant_profile and self.assistant_profile is not None:
            if type(self.assistant_profile) == str:
                content = content + "\n\n### Your profile: \n" + self.assistant_profile
            elif type(self.assistant_profile) == dict:
                content = content + "\n\n### Your profile: \n" + dict_to_str(self.assistant_profile, bullet = "\t - ")
            else:
                raise ChatbotInputError("assistant_profile must be a string or a dictionary")
            
        if use_user_profile and self.user_profile is not None:
            if type(self.user_profile) == str:
                content = content + "\n\n### user profile: \n" + self.user_profile
            elif type(self.user_profile) == dict:
                content = content + "\n\n### user profile: \n" + dict_to_str(self.user_profile, bullet = "\t - ")
            else:
                raise ChatbotInputError("user_profile must be a string or a dictionary")
            
        return content
        

class FlowGuideSystemChat(SystemChat):
    """
    system chat for flow guide

    - flow_guide : flow guide of the chatbot
    """

    def __init__(self, flow_guide: str):
        """
        system chat for flow guide
        
        :param flow_guide: detailed instruction for the flow of the chatbot
        => ex: "Let's turn the topic to the weather."
        """
        super().__init__(flow_guide)
        self.flow_guide = flow_guide


class GuidanceSystemChat(SystemChat):
    """
    system chat for guiding agent
    """

    def __init__(self, guidance: str):
        """
        system chat for guiding agent

        :param guiding_content: detailed instruction for guiding the agent
        => ex: "let's move to next topic: favorite movies"
        """
        self.guidance = guidance

        super().__init__(f"guidance : {guidance}")
        

    







def chatObjs_to_list(chatObjs: list[ChatObj]) -> list[dict]:
    """
    convert list of chat objects to list of dicts

    :param chatObjs: list[ChatObj]
    :return: list[dict]
    """
    return [chatObj.chat() for chatObj in chatObjs]
