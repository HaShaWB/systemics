# graphAgent/flowEdge.py

import asyncio
from typing import Callable,  TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .stateNode import StateNode

from .graphAgentError import NotConnectedNodeError
from .stateInfo import StateInfo, AgentEvent


class FlowEdge(ABC):

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"]):

        self.prev_state = prev_state
        self.candidate_states = candidate_states

    def return_next_state(self, state: "StateNode"):

        if state in self.candidate_states:
            return state
        else:
            raise NotConnectedNodeError("The state is not a candidate state of this edge.")


    @abstractmethod
    def forward(self, state_info: StateInfo) -> "StateNode":
        pass



class SimpleLogicalEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 condition_func: Callable[..., bool]):

        super().__init__(prev_state, [candidate_state])

        self.condition_func = condition_func


    def forward(self, state_info: StateInfo) -> "StateNode":

        if self.condition_func(state_info):
            return self.candidate_states[0]
        else :
            return None



class BranchLogicalEdge(FlowEdge):

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"]):
        
        super().__init__(prev_state, candidate_states)

        self.decision_func = decision_func


    def forward(self, state_info: StateInfo) -> "StateNode":

        return self.return_next_state(self.decision_func(state_info))



class SimpleTimerEdge(FlowEdge):

    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 condition_func: Callable[..., bool], time: float):

        super().__init__(prev_state, [candidate_state])

        self.condition_func = condition_func
        self.time = time
        self._timer_task = None  


    async def start_timer(self):

        self._timer_task = asyncio.create_task(self._run_timer())


    async def _run_timer(self):

        await asyncio.sleep(self.time)
        return


    def stop_timer(self):

        if self._timer_task is not None:
            self._timer_task.cancel()


    async def forward(self, state_info: StateInfo) -> "StateNode":

        await self.start_timer()

        try:
            await self._timer_task 
            if self.condition_func(state_info):
                return self.candidate_states[0]
            else:
                return None
        except asyncio.CancelledError:
            return None



class BranchTimerEdge(FlowEdge):

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"], time: int):
        
        super().__init__(prev_state, candidate_states)
        self.decision_func = decision_func
        self.time = time
        self._timer_task = None


    async def start_timer(self):

        self._timer_task = asyncio.create_task(self._run_timer())


    async def _run_timer(self):

        await asyncio.sleep(self.time)
        return


    def stop_timer(self):

        if self._timer_task is not None:
            self._timer_task.cancel()


    async def forward(self, state_info: StateInfo) -> "StateNode":
        
        await self.start_timer()
        try:
            await self._timer_task
            return self.return_next_state(self.decision_func(state_info))
        except asyncio.CancelledError:
            return None
    

    
class SimpleEventEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 event_cue: str):

        super().__init__(prev_state, [candidate_state])

        self.event_cue = event_cue

    
    def forward(self, state_info: StateInfo) -> "StateNode":
        for event in state_info.flow_event_list:
            if event.event_cue == self.event_cue:
                state_info.flow_event_list.remove(event)
                return self.candidate_states[0]
        return None

    

class BranchEventEdge(FlowEdge):
    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"], event_cue: str):

        super().__init__(prev_state, candidate_states)

        self.decision_func = decision_func
        self.event_cue = event_cue


    def forward(self, state_info: StateInfo) -> "StateNode":
        for event in state_info.flow_event_list:
            if event.event_cue == self.event_cue:
                state_info.flow_event_list.remove(event)
                return self.return_next_state(self.decision_func(state_info, event.event_data))
        return None


