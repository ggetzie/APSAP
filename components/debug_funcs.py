 
 
import scipy.optimize as opt
 
from PyQt5 import uic
 
 
 

import pathlib
import open3d as o3d
import re
from database_tools import get_pottery_sherd_info, update_match_info
from glob import glob as glob
from database_tools import get_all_pottery_sherd_info

import json
import numpy as np
import time
 
 
 
from misc import simple_get_json, simple_save_json
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
HEMISPHERES = ("N", "S")



# Here let's do some simple machine learning to get


class DebugFuncs():






    def generate_data(self):
        for_ml = simple_get_json("./for_ml.json")
        current = time.time()
        _3d_object ={}

        for data in self.json_data["past_records"]:
            key =  f'{data["utm_easting"]}-{data["utm_northing"]}-{data["hemisphere"]}-{data["zone"]}-{data["context"]}-{int(data["batch_num"])}-{data["piece_num"]}'  
           
            _3d_object[key] = data

        sherds = (get_all_pottery_sherd_info())
        non_sherds = [x for x in sherds if x[12]!= None and x[13]!=None]

        for i in non_sherds:
            key=f"{i[2]}-{i[3]}-{i[0]}-{i[1]}-{i[4]}-{i[11]}-{i[12]}"
            res = (
            self.file_root
            / self.hemisphere_cb.currentText()
            / self.zone_cb.currentText()
            / self.easting_cb.currentText()
            / self.northing_cb.currentText()
            / self.context_cb.currentText()
            )
            if key in _3d_object: #This means we have a 2d_pic matching a 3d model
                res = ( self.file_root/ str(i[0])/ str(i[1])/  str(i[2])/ str(i[3])/  str(i[4]))
                _2d_pic_id = i[5]
                _2d_image_path_image_1 = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "1.jpg"
                _2d_image_path_image_2 = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "2.jpg"
                if pathlib.Path(_2d_image_path_image_1).is_file() and pathlib.Path(_2d_image_path_image_2).is_file():

                    
                    
                    _3d_object_info = _3d_object[key]
                    _3d_area = _3d_object_info["area"]
    
                    _3d_color = _3d_object_info["colors_summary"]
                    width_length_3d = _3d_object_info["width_length_summary"]
                        
                    color_brightness_3d = (_3d_object_info["brightness_summary"][3]) 
                    color_brightness_std_3d = (_3d_object_info["brightness_summary"][-1]) 

                    #print(_3d_object[key])

                    
                                    #Area based similiarity
                    _2d_area_image_1 = self.comparator.get_2d_picture_area(_2d_image_path_image_1)
                    _2d_area_image_2 = self.comparator.get_2d_picture_area(_2d_image_path_image_2)    
                    #Brightness based simliarity
                    color_brightness_2d_image_2 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_2)
                    color_brightness_2d_image_1 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_1)
                    

                    #Let's do the third one: color based similarity
                    #Prepare the colors summaries for these two pictures
                    #Not that useful we found out.
                    front_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_1))
                    back_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_2))  
                    
                    #Fourth one, width length
                    _2d_width_length_image_1 = (self.comparator.get_2d_width_length(_2d_image_path_image_1))
                    _2d_width_length_image_2 = (self.comparator.get_2d_width_length(_2d_image_path_image_2)) 
                    area_similarity = min( max(_3d_area/_2d_area_image_2, _2d_area_image_2/_3d_area) , max(_3d_area/_2d_area_image_1, _2d_area_image_1/_3d_area))
                    brightness_similarity = min( max((color_brightness_2d_image_2[3]/1.2)/color_brightness_3d, color_brightness_3d/(color_brightness_2d_image_2[3]/1.2)) , max(color_brightness_3d/(color_brightness_2d_image_1[3]/1.2), (color_brightness_2d_image_1[3]/1.2)/color_brightness_3d))
                    brightness_std_similarity = min( max((color_brightness_2d_image_2[-1]/2.1)/color_brightness_std_3d, color_brightness_std_3d/(color_brightness_2d_image_2[-1]/2.1)) , max(color_brightness_std_3d/(color_brightness_2d_image_1[-1]/2.1), (color_brightness_2d_image_1[-1]/2.1)/color_brightness_std_3d))
                    color_similarity = self.comparator.get_color_difference(front_color, back_color  ,_3d_color)          
                    width_length_simlarity_with_image_1  = (max (width_length_3d[0]/_2d_width_length_image_1[0],_2d_width_length_image_1[0]/  width_length_3d[0]) +  max (width_length_3d[1]/_2d_width_length_image_1[1],_2d_width_length_image_1[1]/  width_length_3d[1]))/2
                    width_length_simlarity_with_image_2  = (max (width_length_3d[0]/_2d_width_length_image_2[0],_2d_width_length_image_2[0]/  width_length_3d[0]) +  max (width_length_3d[1]/_2d_width_length_image_2[1],_2d_width_length_image_2[1]/  width_length_3d[1]))/2
                    width_length_simlarity = min (width_length_simlarity_with_image_1, width_length_simlarity_with_image_2)
                    #all_similarities = np.array([area_similarity, brightness_similarity, width_length_simlarity,  brightness_std_similarity, color_similarity])
                    calculuated = [area_similarity, brightness_similarity, width_length_simlarity,  brightness_std_similarity, color_similarity]
                    for_ml["data"].append({"cal": calculuated, "path": str(res)})


                    #multipliers = np.array([90, 65, 40,5, 0.15])
                    #result = np.dot(all_similarities, multipliers) /np.sum(multipliers) #Now we reduce it to a number close to 1, the closer it is to one, the more accurate the prediction it is.
                    #print(result)
                    #print(self.get_3d_2d_simi(color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ))
                    print(_2d_image_path_image_1)
                    print(_2d_image_path_image_2)
                    print()
        simple_save_json(for_ml, "./for_ml.json")
        print(f"Timed passed: {time.time() - current} seconds")
        #('N', 38, 478130, 4419430, 128, 74, 'pottery', 'body', None, '2b2e382f-b307-4bb5-a01b-23618b47573b', 2022, 19, 7, False)
