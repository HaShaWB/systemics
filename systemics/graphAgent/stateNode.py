# graphAgent/stateNode.py

import asyncio

from .stateInfo import StateInfo
from .flowEdge import *


TIME_OUT = 30
TICK = 1 / 30



class StateNode:

    def __init__(self, state_name: str, state_description: str = "", state_info: StateInfo = None):

        self.state_name = state_name
        self.state_description = state_description
        self.state_info = state_info

        self.candidate_states : dict[str, StateNode] = {
            "logical" : [],
            "timer" : [],
            "event" : []
        }

        self.logical_edges : list[SimpleLogicalEdge|BranchLogicalEdge] = []
        self.timer_edge : SimpleEventEdge|BranchTimerEdge = SimpleTimerEdge(self, self, lambda x : True, TIME_OUT)
        self.event_edges : list[SimpleEventEdge|BranchEventEdge] = []


    def action(self,):
        pass


    def set_logical_edges(self, logical_edges: list[SimpleLogicalEdge|BranchLogicalEdge] ):

        self.logical_edges = logical_edges
        temp = []
        for edge in logical_edges:
            temp.append(edge.candidate_states)
        self.candidate_states['logical'] = temp


    def set_timer_edge(self, timer_edge: SimpleEventEdge|BranchTimerEdge):

        self.timer_edge = timer_edge
        self.candidate_states['timer'] = timer_edge.candidate_states


    def set_event_edges(self, event_edges: list[SimpleEventEdge|BranchEventEdge]):

        self.event_edges = event_edges
        temp = []
        for edge in event_edges:
            temp.append(edge.candidate_states)
        self.candidate_states['event'] = temp


    def clear_edges(self, edge_type: str):

        if edge_type == "logical":
            self.logical_edges.clear()
        elif edge_type == "timer":
            self.timer_edge = SimpleTimerEdge(self, self, lambda x : True, TIME_OUT)
        elif edge_type == "event":
            self.event_edges.clear()


    async def process(self):

        self.action()

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
