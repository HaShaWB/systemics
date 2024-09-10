import os
from pydantic import BaseModel

import openai

from LM import LM


class Openai_LM(LM):
    """
    Openai api 기반 Language Model
    """

    def __init__(self, model: str, api_key: str = os.getenv('OPENAI_API_KEY')):
        """
        :param model: openai의 LM 모델명 => gpt-4o, gpt-3.5-turbo 등
        :param api_key: openai api key => 기본값 = 시스템 환경 변수의 값을 가져옴
        """
        self.model = model
        self.agent = openai.OpenAI(api_key=api_key)

    def generate_chat(self,
                      messages: list,
                      temperature: float = 1,
                      top_p: float = 1,
                      max_tokens: int | None = None,
                      **kwargs):
        """
        messages를 바탕으로 assistant의 답변을 생성하는 함수
        :param messages: 기존의 대화록
        :param temperature: 답변의 랜덤성 (커질수록 무작위한 답변이 나옴)
        :param top_p: 답변의 범위 (커질수록 다양한 답변이 나옴)
        :param max_tokens: 최대 사용 토큰 수
        :param kwargs: 기타 key words
        :return: answer, # of used tokens
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
        messages를 바탕으로 json 형식에 맞춰 답변을 생성하는 함수
        :param messages: 기존의 대화록
        :param temperature: 답변의 랜덤성 (커질수록 무작위한 답변이 나옴)
        :param top_p: 답변의 범위 (커질수록 다양한 답변이 나옴)
        :param max_tokens: 최대 사용 토큰 수
        :param kwargs: 기타 key words
        :return: answer(in json), # of used tokens
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
                                   structure: BaseModel,
                                   temperature: float = 1,
                                   top_p: float = 1,
                                   max_tokens: int | None = None,
                                   **kwargs
                                   ):
        """
        messages를 바탕으로 특정한 structure에 맞춰 답변을 생성하는 함수
        :param messages: 기존의 대화록
        :param structure: 답변 structure
        :param temperature: 답변의 랜덤성 (커질수록 무작위한 답변이 나옴)
        :param top_p: 답변의 범위 (커질수록 다양한 답변이 나옴)
        :param max_tokens: 최대 사용 토큰 수
        :param kwargs: 기타 key words
        :return: answer(in BaseModel -> use .json() or .dict()), # of used tokens
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
