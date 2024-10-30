from abc import ABC, abstractmethod
from pydantic import BaseModel


class LM(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def generate_chat(self,
                      messages: list,
                      temperature: float = 1,
                      top_p: float = 1,
                      max_tokens: int | None = None,
                      **kwargs) -> tuple[str, dict]:
        pass


class Openai_LM(LM):
    """
    Language Model based on OpenAI API
    """

    def __init__(self, model: str, api_key: str = None):
        """
        Initialize the OpenAI Language Model

        :param model: Name of the OpenAI LM model (e.g., gpt-4, gpt-3.5-turbo)
        :param api_key: OpenAI API key (default: retrieves from system environment variable)
        """

        import openai
        
        self.model = model
        self.agent = openai.OpenAI(api_key=api_key)

    def generate_chat(self,
                      messages: list,
                      temperature: float = 1,
                      top_p: float = 1,
                      max_tokens: int | None = None,
                      **kwargs):
        """
        Generate assistant's response based on the given messages

        :param messages: List of previous conversation messages
        :param temperature: Controls randomness in the response (higher values increase randomness)
        :param top_p: Controls diversity of the response (higher values increase diversity)
        :param max_tokens: Maximum number of tokens to generate
        :param kwargs: Additional keyword arguments
        :return: Tuple containing (generated answer, usage statistics)
        """
        completion = self.agent.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            **kwargs
        )

        usage = completion.usage
        answer = completion.choices[0].message.content

        return answer, usage


    def generate_chat_in_json(self,
                              messages: list,
                              temperature: float = 1,
                              top_p: float = 1,
                              max_tokens: int | None = None,
                              **kwargs):
        """
        Generate response in JSON format based on the given messages

        :param messages: List of previous conversation messages
        :param temperature: Controls randomness in the response (higher values increase randomness)
        :param top_p: Controls diversity of the response (higher values increase diversity)
        :param max_tokens: Maximum number of tokens to generate
        :param kwargs: Additional keyword arguments
        :return: Tuple containing (generated answer in JSON format, usage statistics)
        """

        completion = self.agent.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            **kwargs
        )

        answer = completion.choices[0].message.content
        usage = completion.usage

        return answer, usage


    def generate_chat_in_structure(self,
                                   messages: list,
                                   structure: "BaseModel",
                                   temperature: float = 1,
                                   top_p: float = 1,
                                   max_tokens: int | None = None,
                                   **kwargs
                                   ):
        """
        Generate response in a specific structure based on the given messages

        :param messages: List of previous conversation messages
        :param structure: Desired response structure (BaseModel)
        :param temperature: Controls randomness in the response (higher values increase randomness)
        :param top_p: Controls diversity of the response (higher values increase diversity)
        :param max_tokens: Maximum number of tokens to generate
        :param kwargs: Additional keyword arguments
        :return: Tuple containing (generated answer in specified structure, usage statistics)
        """

        completion = self.agent.beta.chat.completions.parse(
            model=self.model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            response_format=structure,
            **kwargs
        )

        answer = completion.choices[0].message.parsed
        usage = completion.usage

        return answer, usage
