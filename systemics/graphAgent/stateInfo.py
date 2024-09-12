# graphAgent/StateInfo.py

class AgentEvent:
    def __init__(self, event_cue, event_data):
        self.event_cue = event_cue
        self.event_data = event_data

    def __eq__(self, other):
        return self.event_cue == other.event_cue


class StateInfo:
    def __init__(self):
        self.flow_event_list: list[AgentEvent] = []
