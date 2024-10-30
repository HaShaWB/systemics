from abc import ABC, abstractmethod


class Face_Embedding(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def embed_face(self):
        pass


class DeepFace_Embedding(Face_Embedding):
    def __init__(self, model_name):
        """
        :param model_name: model name of deepface (Facenet, Facenet512, ...)
        """
        from deepface import DeepFace
        self.model = DeepFace
        self.model_name = model_name

    
    def embed_face(self, image):
        """
        embed face from image (by deepface)
        :param image_path: image path
        :return: face embedding
        """
        return self.model.represent(image, model_name=self.model_name)
        
    
    def embed_face_from_file(self, file_path):
        """
        embed face from image (by deepface)
        """
        return self.embed_face(file_path, model_name=self.model_name)