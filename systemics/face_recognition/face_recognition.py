from abc import ABC, abstractmethod

import numpy as np


class Face_Recognition(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def embed_face(self):
        pass


class DeepFace_Recognition(Face_Recognition):
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
        :param image: image (in BGR or BASE64)
        :return: face embedding
        """
        return self.model.represent(image, model_name=self.model_name)
        
    
    def embed_face_from_file(self, file_path):
        """
        embed face from image (by deepface)
        """
        return self.embed_face(file_path, model_name=self.model_name)
    

    def make_face_index(self, image_folder_path):
        """
        make face index from image folder (by deepface)
        :param image_folder_path: image folder path
        :return: face index
        """

        empty_image = np.full((160, 160, 3), 255, dtype=np.uint8)


        return self.model.find(empty_image, image_folder_path, model_name=self.model_name)


    def find_face(self, image_path, image_folder_path):
        """
        find face from image (by deepface)
        :param image_path: image path
        :param image_folder_path: image folder path
        :return: face embedding
        """
        return self.model.find(image_path, image_folder_path, model_name=self.model_name)