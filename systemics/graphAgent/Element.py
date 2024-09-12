import asyncio
import queue
from typing import Callable, Any

TICK = 1 / 30


class StateInfo:
    def __init__(self):
        """
        State 내의 상태 정보를 담은 클래스 -> 한 그래프 당 1개
        - event_queue: Edge Event 처리를 위한 Queue
        """
        self.event_queue = queue.Queue()


class FlowEdge:
    def __init__(self, prev_state: "StateNode", next_state: "StateNode", description: str = ""):
        """
        제일 기본적인 flow edge
        :param prev_state: 이전(현재) node
        :param next_state: 다음 node
        :param description: 디버그 용 간단한 설명
        """
        self.prev_state = prev_state
        self.next_state = next_state
        self.description = description

    def forward(self, stateInfo: StateInfo) -> "StateNode":
        """
        다음 상태 node를 반환
        
        :param stateInfo: state 정보
        :return: 다음 node
        """
        return self.next_state


class LogicalEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", next_state: "StateNode",
                 condition_func: Callable[..., bool], description: str = ""):
        """
        간단한(few latency) 논리적 조건을 기반으로 하는 edge
        
        :param prev_state: 이전 상태 (현재 상태)
        :param next_state: 다음 상태 (후보)
        :param condition_func: true -> 다음 상태로 이동, false -> 이동 x
        :param description: 간단한 설명 (개발용) 
        """
        super().__init__(prev_state, next_state, description)
        self.condition_func = condition_func

    def forward(self, stateInfo: StateInfo) -> "StateNode":
        """
        다음 node로의 진행 결정
        - condition_func을 호출하여 다음 상태로 이동할지 결정
            - 이동 : 다음 상태 node
            - 이동 x : None
        
        :param stateInfo: state 정보
        :return: 다음 node or None
        """
        return self.next_state if self.condition_func(stateInfo) else None


class EventEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", next_state: "StateNode",
                 event_cue: str, description: str = ""):
        """
        이벤트를 기반으로 하는 edge
        
        :param prev_state: 이전 상태 (현재 상태) 
        :param next_state: 다음 상태 (후보)
        :param event_cue: 이벤트 코드 -> stateInfo의 evnet_queue를 통해 지정
        :param description: 간단한 설명(개발용)
        """
        super().__init__(prev_state, next_state, description)
        self.event_cue = event_cue

    async def forward(self, stateInfo: StateInfo) -> "StateNode":
        """
        다음 node로의 진행 결정
            - stateInfo의 event_queue를 통해 이벤트 처리 및 다음 상태 결정
            - event_queue에 event_cue가 있으면 다음 상태로 이동
            - event_cue가 발생할 때까지 대기
            
        :param stateInfo: state 정보
        :return: 다음 node or 무한 대기
        """
        while True:
            if not stateInfo.event_queue.empty():
                event = stateInfo.event_queue.get()
                if event == self.event_cue:
                    return self.next_state
                stateInfo.event_queue.put(event)
            await asyncio.sleep(TICK)


class TimerEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", next_state: "StateNode",
                 duration: float, description: str = ""):
        """
        시간을 기반으로 하는 edge
        - 일정 시간 후에 다음 상태로 이동
        
        :param prev_state: 이전 상태 (현재 상태)
        :param next_state: 다음 상태 (후보)
        :param duration: delay 시간
        :param description: 간단한 설명(개발용)
        """
        super().__init__(prev_state, next_state, description)
        self.duration = duration

    async def forward(self, stateInfo: StateInfo) -> "StateNode":
        """
        다음 node로의 진행 결정
            - duration 시간 후에 다음 상태로 이동
            
        :param stateInfo: state 정보
        :return: 다음 node
        """
        await asyncio.sleep(self.duration)
        return self.next_state


class StateNode:
    def __init__(self, state_name: str, state_description: str = ""):
        """
        state를 표현하는 node
        
        :param state_name: state 이름
        :param state_description: state 설명
        """
        
        self.state_name = state_name
        self.state_description = state_description
        self.logical_edges: list[LogicalEdge] = []
        self.timer_edge: TimerEdge = None
        self.event_edges: list[EventEdge] = []
        self.connected_nodes = set()

    def action(self, stateInfo: StateInfo) -> None:
        """
        state node에서 수행할 action을 정의
        
        :param stateInfo: 현재 상태 데이터
        :return: None
        """
        pass

    async def process(self, stateInfo: StateInfo) -> "StateNode":
        """
        state node에서 action을 수행하고 다음 state로 이동할지 결정

        :param stateInfo: 현재 상태 데이터
        :return: 다음 노드
        """
        self.action(stateInfo)

        for edge in self.logical_edges:
            next_state = edge.forward(stateInfo)
            if next_state:
                return next_state

        if self.timer_edge is None and not self.event_edges:
            return self

        event_tasks = [edge.forward(stateInfo) for edge in self.event_edges]

        if self.timer_edge:
            event_tasks.append(self.timer_edge.forward(stateInfo))
        done, pending = await asyncio.wait(event_tasks, return_when=asyncio.FIRST_COMPLETED)

        next_state = done.pop().result()
        for task in pending:
            task.cancel()

        return next_state
