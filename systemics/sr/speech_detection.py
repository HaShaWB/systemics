from collections import deque
from io import BytesIO
from abc import ABC, abstractmethod
import array

from pydub import AudioSegment
import numpy as np


class Speech_Detection(ABC):
    def __init__(self, buffer_size_ms: int = 1000,
                 chunk_size_ms: int = 20,  
                 audio_sample_rate: int = 16000,
                 speech_threadhold: float = 0.5):
        """
        :param buffer_size_ms: the size of the buffer in ms (buffer: temporal window for prediction)
        :param chunk_size_ms: the size of the chunk in ms (chunk: the smallest unit of audio)
        :param audio_sample_rate: the sample rate of the audio
        :param speech_threadhold: the threadhold for speech detection (ratio of speech in the buffer)
        """
        self.buffer_size_ms = buffer_size_ms
        self.audio_sample_rate = audio_sample_rate
        self.chunk_size_ms = chunk_size_ms
        self.speech_threadhold = speech_threadhold

        self.chunk_size = int(self.audio_sample_rate * self.chunk_size_ms / 1000)
        self.buffer_size = int(self.audio_sample_rate * self.buffer_size_ms / 1000)

        self.audio_buffer = deque(maxlen=self.buffer_size)
        self.speech_bool_buffer = deque(maxlen=self.buffer_size)

        self.speech_count = 0


    @abstractmethod
    def unit_speech_detection(self, chunk: np.ndarray) -> bool:
        """
        predict if the chunk is speech or not
        """
        pass

    
    def add_chunk(self, chunk: np.ndarray):
        is_speech = self.unit_speech_detection(chunk)

        if len(self.audio_buffer) >= self.buffer_size:
            was_speech = self.speech_bool_buffer.popleft()
            if was_speech:
                self.speech_count -= 1
            if is_speech:
                self.speech_count += 1

        else:
            if is_speech:
                self.speech_count += 1

        self.audio_buffer.append(chunk)
        self.speech_bool_buffer.append(is_speech)


    def detection(self) -> bool:
        """
        predict if the buffer is speech or not
        """
        return self.speech_count / len(self.audio_buffer) > self.speech_threadhold
    

    def get_audio_in_array(self):
        return np.concatenate(self.audio_buffer)
    

    def get_audio_in_wav(self):
        audio = self.get_audio_in_array()
        raw_data = array.array('h', audio).tobytes()
        
        audio_segment = AudioSegment(
            raw_data,
            frame_rate=self.audio_sample_rate,
            sample_width=2,
            channels=1
        )
        
        wav_buffer = BytesIO()
        audio_segment.export(wav_buffer, format='wav')
        wav_buffer.seek(0)
        return wav_buffer.read()
    

    def get_audio_in_mp3(self):
        audio = self.get_audio_in_array()
        raw_data = array.array('h', audio).tobytes()
        
        audio_segment = AudioSegment(
            raw_data,
            frame_rate=self.audio_sample_rate,
            sample_width=2,
            channels=1
        )
        
        mp3_buffer = BytesIO()
        audio_segment.export(mp3_buffer, format='mp3')
        mp3_buffer.seek(0)
        return mp3_buffer.read()
    

    
class VAD(Speech_Detection):
    def __init__(self, buffer_size_ms: int = 1000,
                 chunk_size_ms: int = 20,  
                 audio_sample_rate: int = 16000,
                 speech_threadhold: float = 0.5,
                 vad_mode: int = 3):
        """
        :param buffer_size_ms: the size of the buffer in ms (buffer: temporal window for prediction)
        :param chunk_size_ms: the size of the chunk in ms (chunk: the smallest unit of audio)
        :param audio_sample_rate: the sample rate of the audio
        :param speech_threadhold: the threadhold for speech detection (ratio of speech in the buffer)
        :param vad_mode: the mode of the VAD (0: normal, 1: low bit rate, 2: aggressive, 3: very aggressive)
        """
        super().__init__(buffer_size_ms, chunk_size_ms, audio_sample_rate, speech_threadhold)
        self.vad_mode = vad_mode

        import webrtcvad
        self.vad = webrtcvad.Vad(self.vad_mode)


    def unit_speech_detection(self, chunk: np.ndarray) -> bool:
        return self.vad.is_speech(chunk, self.audio_sample_rate)