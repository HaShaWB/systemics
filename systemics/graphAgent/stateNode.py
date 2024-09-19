# graphAgent/stateNode.py

import asyncio

from .stateInfo import StateInfo
from .flowEdge import *

TIME_OUT = 30
TICK = 1 / 30

class StateNode:
    """
    Represents a state node in the graph

    - state_name: name of the state
    - state_description: description of the state
    - state_info: information about the state
    - candidate_states: dictionary of candidate states for different edge types
    - logical_edges: list of logical edges
    - timer_edge: timer edge
    - event_edges: list of event edges
    """

    def __init__(self, state_name: str, state_description: str = "", state_info: StateInfo = None, action: callable[StateInfo, None] = lambda x: None):
        """
        Initialize a StateNode

        :param state_name: name of the state
        :param state_description: description of the state (optional)
        :param state_info: information about the state (optional)
        :param action: action to perform when entering the state (optional)
        """
        self.state_name = state_name
        self.state_description = state_description
        self.state_info = state_info
        self.action = action

        self.candidate_states : dict[str, StateNode] = {
            "logical" : [],
            "timer" : [],
            "event" : []
        }

        self.logical_edges : list[SimpleLogicalEdge|BranchLogicalEdge] = []
        self.timer_edge : SimpleEventEdge|BranchTimerEdge = SimpleTimerEdge(self, self, lambda x : True, TIME_OUT)
        self.event_edges : list[SimpleEventEdge|BranchEventEdge] = []


    def set_logical_edges(self, logical_edges: list[SimpleLogicalEdge|BranchLogicalEdge] ):
        """
        Set the logical edges for this state

        :param logical_edges: list of logical edges
        """
        self.logical_edges = logical_edges
        temp = []
        for edge in logical_edges:
            temp.append(edge.candidate_states)
        self.candidate_states['logical'] = temp

    def set_timer_edge(self, timer_edge: SimpleEventEdge|BranchTimerEdge):
        """
        Set the timer edge for this state

        :param timer_edge: timer edge
        """
        self.timer_edge = timer_edge
        self.candidate_states['timer'] = timer_edge.candidate_states

    def set_event_edges(self, event_edges: list[SimpleEventEdge|BranchEventEdge]):
        """
        Set the event edges for this state

        :param event_edges: list of event edges
        """
        self.event_edges = event_edges
        temp = []
        for edge in event_edges:
            temp.append(edge.candidate_states)
        self.candidate_states['event'] = temp

    def clear_edges(self, edge_type: str):
        """
        Clear edges of a specific type

        :param edge_type: type of edge to clear ("logical", "timer", or "event")
        """
        if edge_type == "logical":
            self.logical_edges.clear()
        elif edge_type == "timer":
            self.timer_edge = SimpleTimerEdge(self, self, lambda x : True, TIME_OUT)
        elif edge_type == "event":
            self.event_edges.clear()

    async def process(self):
        """
        Process the current state and determine the next state

        :return: next state node
        """
        self.action(self.state_info)

        state_info = self.state_info

        for edge in self.logical_edges:
            next_state = edge.forward(state_info)
            if next_state:
                return next_state
            
        timer_next_state = self.timer_edge.forward(state_info)

        while(True):
            if timer_next_state:
                return timer_next_state
            for event_edge in self.event_edges:
                next_state = event_edge.forward(state_info)
                if next_state:
                    self.timer_edge.stop_timer()
                    return next_state
            await asyncio.sleep(TICK)
