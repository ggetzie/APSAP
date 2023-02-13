
import numpy as np
from PIL import Image
import cv2
import json



class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
        
class FileIOModelMixin:

    def open_image(self, image_path, full_size):
        if full_size == True:
            return  (Image.open(image_path))
        else:
            return  Image.open(image_path).resize((450,300), Image.ANTIALIAS)
        #(Image.fromarray(cv2.cvtColor(cv2.resize((cv2.imread(image_path) ),(450, 300)),cv2.COLOR_BGR2RGB)))


    def simple_get_json(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data



    def simple_save_json(self, json_object, json_file):
        with open(json_file, 'w') as f:
            json.dump(json_object, f, cls=NpEncoder)