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
    def open_image(self, image_path, full_size):
        if full_size == True:
            return Image.open(image_path)
        else:
            return Image.open(image_path).resize((450, 300), Image.ANTIALIAS)

    def simple_get_json(self, json_file):
        f = open(json_file)
        data = json.load(f)
        return data

    def simple_save_json(self, json_object, json_file):
        with open(json_file, "w") as f:
            json.dump(json_object, f, cls=NpEncoder)

    def get_all_plys(self):
        ply_paths = []
        for hemisphere_path in hemisphere_paths:
            zone_paths = glob(str(PurePath(hemisphere_path)/"*"))
        
            for zone_path in zone_paths:
                easting_paths = glob(str(PurePath(zone_path)/"*"))

        
                for easting_path in easting_paths:
                    northing_paths = glob(str(PurePath(easting_path)/"*"))
                    
                    for northing_path in northing_paths:
                        context_paths = glob(str(PurePath(northing_path)/"*"))
                        
                        for context_path in context_paths:
                            finds_folder = PurePath(context_path)/"finds"

                            _3d_batch_folder = finds_folder/"3dbatch"
                            years_in_3d_batch = glob(str(_3d_batch_folder/"*"))
                            for year in years_in_3d_batch:
                                batch_xxxs =  glob(str(PurePath(year)/"batch_*"))
                                for batch in batch_xxxs:
                                    ply_folder = PurePath(batch)/"registration_reso1_maskthres242/final_output"
                                    plys = glob(str(ply_folder/"piece_*_world.ply"))
                                    for ply in plys:
                                        ply_paths.append(ply)
        return ply_paths

