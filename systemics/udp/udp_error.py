# udp/udp_error.py

class UDPError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class UDPConnectionError(UDPError):
    def __init__(self, message: str):
        super().__init__(message)
