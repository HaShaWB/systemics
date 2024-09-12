# graphAgent/graphAgentError.py

class GraphAgentError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotConnectedNodeError(GraphAgentError):
    def __init__(self, message):
        super().__init__(message)