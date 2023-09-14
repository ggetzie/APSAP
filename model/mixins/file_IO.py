import numpy as np
from PIL import Image
import cv2
import json
from glob import glob 
from pathlib import Path, PurePath
FILE_ROOT = PurePath("D:/ararat/data/files")
import os 
import json
hemisphere_paths = glob( str(FILE_ROOT / "N")) + glob( str(FILE_ROOT / "S")) 

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

class FileIOMixin:
    def open_image(self, image_path):
        return Image.open(image_path).resize((450, 300), Image.ANTIALIAS)

    def simple_get_json(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data

    def simple_save_json(self, json_object, json_file):
        with open(json_file, "w") as f:
            json.dump(json_object, f, cls=NpEncoder)

