import numpy as np
from PIL import Image
import json


class NpEncoder(json.JSONEncoder):
    """This class is used for serializing the json object when it is used to save it"""

    def default(self, o):
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super(NpEncoder, self).default(o)


class FileIOMixin:
    def open_image(self, image_path):
        """This functions open an image in 450 x 300.

        Args:
            image_path (str): The path of the image to be opened

        Returns:
            Pillow Image: A Pil image object
        """
        return Image.open(image_path).resize((450, 300), Image.ANTIALIAS).convert("RGB")

    def simple_get_json(self, json_path):
        """This function loads the json path in to a python object

        Args:
            json_path (str): a path to a valid json

        Returns:
            json object: A json object containing content from the json path
        """
        f = open(json_path, encoding="utf-8")
        data = json.load(f)
        return data

    def simple_save_json(self, json_object, json_path):
        """This function saves the json object into the json file path

        Args:
            json_object (Json Object): The json object to be saved
            json_path (str): The path to the json file to be saved to
        """
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_object, f, cls=NpEncoder)
