from abc import ABC, abstractmethod

class STT(ABC):
    def __init__(self, model_name: str):
        self.model = model_name

    @abstractmethod
    def transcribe_from_file(self, file_path: str) -> str:
        """
        Transcribe the speech from the given file
        :param file_path: Path to the audio file
        :return: Transcribed text
        """
        pass


    @abstractmethod
    def transcribe_from_bytes(self, audio_bytes: bytes) -> str:
        """
        Transcribe the speech from the given audio bytes
        :param audio_bytes: Audio bytes to transcribe
        :return: Transcribed text
        """
        pass


class Groq_Whisper(STT):
    def __init__(self, model_name, api_key=None, prompt=None):
        """
        :param model_name: Name of the model
        :param api_key: API key for Groq
        :param prompt: Prompt for the transcription (only whisper)
        """
        super().__init__(model_name)
        self.api_key = api_key
        
        from groq import Groq

        self.client = Groq(api_key=api_key)

    
    def transcribe_from_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            audio_bytes = f.read()
            result = self.client.audio.transcriptions.create(
                model=self.model,
                file=(file_path, audio_bytes)
            )

        return result.text
    

    def transcribe_from_bytes(self, audio_bytes: bytes, format: str = "wav") -> str:
        """
        :param audio_bytes: Audio bytes to transcribe
        :param format: Format of the audio file (wav, mp3, etc.)
        """

        result = self.client.audio.transcriptions.create(
            model=self.model,
            file=("temp." + format, audio_bytes)
        )
    
        
        