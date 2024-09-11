import asyncio
from abc import ABC, abstractmethod
from typing import Callable, Any

TICK = 1 / 30


class LogicalEdge:
    def __init__(self, prev_state: "StateNode", next_state: "StateNode",
                 condition_func: Callable[..., bool], description: str = ""):
        """
        간단한 (few latency) 논리적 조건을 기반으로 하는 edge

        :param prev_state: 이전 상태 (현재 상태)
        :param next_state: 다음 상태 (후보)
        :param condition_func: true -> 다음 상태로 이동, false -> 이동 x
        :param description: 간단한 설명 (개발용)
        """
        self.prev_state = prev_state
        self.next_state = next_state
        self.condition_func = condition_func
        self.description = description

    def forward(self, state_data: Any) -> bool:
        """
        condition_func을 호출하여 다음 상태로 이동할지 결정
        :param state_data: 현재 상태 데이터
        :return: condition_func의 결과
        """
        return self.condition_func(state_data)


class EventEdge(ABC):
    def __init__(self, prev_state: "StateNode", next_state: "StateNode", description: str = ""):
        """
        이벤트를 기반으로 하는 edge

        :param prev_state: 이전 상태 (현재 상태)
        :param next_state: 다음 상태 (후보)
        :param description: 간단한 설명 (개발용)
        """
        self.prev_state = prev_state
        self.next_state = next_state
        self.description = description

    @abstractmethod
    async def forward(self, state_data: Any) -> "StateNode":
        """
        이벤트 처리 및 다음 상태 결정
        :param state_data: 현재 상태 데이터
        :return: 다음 상태 노드
        """
        pass


class StateNode:
    def __init__(self, state_name: str, state_description: str = ""):
        """
        state node 생성자
        :param state_name: state 이름
        :param state_description: state 설명
        """
        self.state_name = state_name
        self.state_description = state_description
        self.logical_edges: list[LogicalEdge] = []
        self.event_edges: list[EventEdge] = []

    def action(self, state_data: Any) -> None:
        """
        state node에서 수행할 action을 정의
        :param state_data: 현재 상태 데이터
        :return: None
        """
        pass

    async def process(self, state_data: Any):
        """
        state node에서 action을 수행하고 다음 state로 이동할지 결정
        :param state_data: 현재 상태 데이터
        :return: 다음 노드
        """
        self.action(state_data)
        for logical_edge in self.logical_edges:
            if logical_edge.forward(state_data):
                return logical_edge.next_state

        events = [event.forward(state_data) for event in self.event_edges]
        done, pending = await asyncio.wait(events, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        return done.pop().result()
