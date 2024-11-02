from PIL import Image
from abc import ABC, abstractmethod

class Human_Cropping(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def crop_person(self, image: str, output_path: str):
        pass



class Yolo_Crop(Human_Cropping):
    def __init__(self, model_name):
        from ultralytics import YOLO
        self.yolo = YOLO(model_name + ".pt")

    
    def crop_person_from_file(self, file_path, output_path = None) -> list:
        """
        crop person from image (by yolo)
        :param file_path: path to the image
        :output_path: path to save the cropped image
        :return: croped images
        """

        img = Image.open(file_path)
        return self.crop_person(img, output_path)
    

    def crop_person(self, image, output_path = None) -> list:
        
        results = self.yolo(image)

        output_imgs = []
        index = 0

        image = Image.open(image)

        for result in results:
            for box in result.boxes:
                if int(box.cls) == 0: 
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    person = image.crop((x1, y1, x2, y2)) 

                    if output_path: 
                        person.save(output_path+str(index)+".jpg")
                    index += 1

                    output_imgs.append(person)

        return output_imgs