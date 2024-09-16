# graphAgent/flowEdge.py

import asyncio
from typing import Callable,  TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from .stateNode import StateNode

from .graphAgentError import NotConnectedNodeError
from .stateInfo import StateInfo, AgentEvent

class FlowEdge(ABC):
    """
    Abstract base class for flow edges

    - prev_state: previous state node
    - candidate_states: list of candidate state nodes
    """

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"]):
        """
        Initialize a FlowEdge

        :param prev_state: previous state node
        :param candidate_states: list of candidate state nodes
        """
        self.prev_state = prev_state
        self.candidate_states = candidate_states

    def return_next_state(self, state: "StateNode"):
        """
        Return the next state if it's a valid candidate

        :param state: potential next state
        :return: validated next state
        :raises NotConnectedNodeError: if the state is not a candidate state
        """
        if state in self.candidate_states:
            return state
        else:
            raise NotConnectedNodeError("The state is not a candidate state of this edge.")

    @abstractmethod
    def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Abstract method to move forward to the next state

        :param state_info: current state information
        :return: next state node
        """
        pass

class SimpleLogicalEdge(FlowEdge):
    """
    A simple logical edge with a single candidate state and a condition function

    - condition_func: function to determine if the edge should be traversed
    """

    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 condition_func: Callable[..., bool]):
        """
        Initialize a SimpleLogicalEdge

        :param prev_state: previous state node
        :param candidate_state: single candidate state node
        :param condition_func: function to determine if the edge should be traversed
        """
        super().__init__(prev_state, [candidate_state])
        self.condition_func = condition_func

    def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward if the condition is met

        :param state_info: current state information
        :return: next state node if condition is met, else None
        """
        if self.condition_func(state_info):
            return self.candidate_states[0]
        else:
            return None

class BranchLogicalEdge(FlowEdge):
    """
    A branching logical edge with multiple candidate states and a decision function

    - decision_func: function to determine which candidate state to choose
    """

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"]):
        """
        Initialize a BranchLogicalEdge

        :param prev_state: previous state node
        :param candidate_states: list of candidate state nodes
        :param decision_func: function to determine which candidate state to choose
        """
        super().__init__(prev_state, candidate_states)
        self.decision_func = decision_func

    def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward based on the decision function

        :param state_info: current state information
        :return: chosen next state node
        """
        return self.return_next_state(self.decision_func(state_info))

class SimpleTimerEdge(FlowEdge):
    """
    A simple timer edge with a single candidate state, condition function, and timer

    - condition_func: function to determine if the edge should be traversed
    - time: duration of the timer
    - _timer_task: asyncio task for the timer
    """

    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 condition_func: Callable[..., bool], time: float):
        """
        Initialize a SimpleTimerEdge

        :param prev_state: previous state node
        :param candidate_state: single candidate state node
        :param condition_func: function to determine if the edge should be traversed
        :param time: duration of the timer in seconds
        """
        super().__init__(prev_state, [candidate_state])
        self.condition_func = condition_func
        self.time = time
        self._timer_task = None

    async def start_timer(self):
        """
        Start the timer as an asyncio task
        """
        self._timer_task = asyncio.create_task(self._run_timer())

    async def _run_timer(self):
        """
        Run the timer
        """
        await asyncio.sleep(self.time)
        return

    def stop_timer(self):
        """
        Stop the timer if it's running
        """
        if self._timer_task is not None:
            self._timer_task.cancel()

    async def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward after the timer expires and if the condition is met

        :param state_info: current state information
        :return: next state node if condition is met after timer, else None
        """
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
    """
    A branching timer edge with multiple candidate states, decision function, and timer

    - decision_func: function to determine which candidate state to choose
    - time: duration of the timer
    - _timer_task: asyncio task for the timer
    """

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"], time: int):
        """
        Initialize a BranchTimerEdge

        :param prev_state: previous state node
        :param candidate_states: list of candidate state nodes
        :param decision_func: function to determine which candidate state to choose
        :param time: duration of the timer in seconds
        """
        super().__init__(prev_state, candidate_states)
        self.decision_func = decision_func
        self.time = time
        self._timer_task = None

    async def start_timer(self):
        """
        Start the timer as an asyncio task
        """
        self._timer_task = asyncio.create_task(self._run_timer())

    async def _run_timer(self):
        """
        Run the timer
        """
        await asyncio.sleep(self.time)
        return

    def stop_timer(self):
        """
        Stop the timer if it's running
        """
        if self._timer_task is not None:
            self._timer_task.cancel()

    async def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward after the timer expires based on the decision function

        :param state_info: current state information
        :return: chosen next state node after timer, or None if cancelled
        """
        await self.start_timer()
        try:
            await self._timer_task
            return self.return_next_state(self.decision_func(state_info))
        except asyncio.CancelledError:
            return None

class SimpleEventEdge(FlowEdge):
    """
    A simple event edge with a single candidate state and an event cue

    - event_cue: string identifier for the event
    """

    def __init__(self, prev_state: "StateNode", candidate_state: "StateNode",
                 event_cue: str):
        """
        Initialize a SimpleEventEdge

        :param prev_state: previous state node
        :param candidate_state: single candidate state node
        :param event_cue: string identifier for the event
        """
        super().__init__(prev_state, [candidate_state])
        self.event_cue = event_cue

    def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward if the event cue is present in the state info

        :param state_info: current state information
        :return: next state node if event cue is present, else None
        """
        for event in state_info.flow_event_list:
            if event.event_cue == self.event_cue:
                state_info.flow_event_list.remove(event)
                return self.candidate_states[0]
        return None

class BranchEventEdge(FlowEdge):
    """
    A branching event edge with multiple candidate states, decision function, and event cue

    - decision_func: function to determine which candidate state to choose
    - event_cue: string identifier for the event
    """

    def __init__(self, prev_state: "StateNode", candidate_states: list["StateNode"],
                 decision_func: Callable[..., "StateNode"], event_cue: str):
        """
        Initialize a BranchEventEdge

        :param prev_state: previous state node
        :param candidate_states: list of candidate state nodes
        :param decision_func: function to determine which candidate state to choose
        :param event_cue: string identifier for the event
        """
        super().__init__(prev_state, candidate_states)
        self.decision_func = decision_func
        self.event_cue = event_cue

    def forward(self, state_info: StateInfo) -> "StateNode":
        """
        Move forward if the event cue is present, based on the decision function

        :param state_info: current state information
        :return: chosen next state node if event cue is present, else None
        """
        for event in state_info.flow_event_list:
            if event.event_cue == self.event_cue:
                state_info.flow_event_list.remove(event)
                return self.return_next_state(self.decision_func(state_info, event.event_data))
        return None


