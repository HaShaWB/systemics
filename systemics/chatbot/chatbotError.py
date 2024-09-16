# chatbot/chatbotError.py

class ChatbotError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ChatbotInputError(ChatbotError):
    def __init__(self, message):
        super().__init__(message)
