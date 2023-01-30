 
 
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
 
import smallestenclosingcircle
from  model.nn_segmentation import MaskPredictor
from misc import open_image
ceremicPredictor =  MaskPredictor("./model/ceremicsmask.pt")
import numpy as np
from PIL import Image, ImageDraw
#https://stackoverflow.com/questions/51696326/extracting-boundary-of-a-numpy-array
from scipy.ndimage import binary_dilation
import smallestenclosingcircle
 
from misc import simple_get_json, simple_save_json
FINDS_SUBDIR = "finds/individual"
BATCH_3D_SUBDIR = "finds/3dbatch"
FINDS_PHOTO_DIR = "photos"
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
HEMISPHERES = ("N", "S")



# Here let's do some simple machine learning to get


class DebugFuncs():

    def get_area_by_pixels(self, image_path, predictor):
        image = open_image(image_path, full_size=False)
        mask = predictor.predict(image)
        mask_array = np.array(mask)
        pixels = np.nonzero(mask_array)
        pixel_area = len(pixels[0])
        return pixel_area
    def get_enclosing_circle_area(self, image_path, predictor):
        image = open_image(image_path, full_size=False)
        mask = predictor.predict(image)
        mask_array = np.array(mask)
        #Here using a technique to leave out only the points of the object consisting of the boundary, so that we have much fewer points to handle
        k = np.ones((3,3),dtype=int)
        boundary_array = binary_dilation(mask_array==0, k) & mask_array
        #Here we get the x, y coordinates of the boundary(which is the non zeros values of the 2d array)
        nonzeros_x_ys = np.nonzero(boundary_array)
        #Tuples of all indices of the boundary
        indices_tuples = list(zip(nonzeros_x_ys[0], nonzeros_x_ys[1]))
        #Below is a nested O(n^2) for loop that gets
        new_li = []
        threshold = 100
        for i in range(len(indices_tuples)): #For each of the tuple, compared it to all the tuples added before, if they are close in distance, don't add to it.
            addable = True
            for pairs in new_li:
                if( (pairs[0] - indices_tuples[i][0])**2  +  (pairs[1] - indices_tuples[i][1])**2  < threshold):
                    addable = False
                    break
            if(addable == True):
                new_li.append(indices_tuples[i])
        center_x, center_y, radius = smallestenclosingcircle.make_circle(new_li)
        return (radius**2 ) * 3.1416

    
 

   
    def adjust_parameters_slope_intercept(self):
        #This fucntion is used to get the data needed for finding the relationship between the 2d image and 3d model
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
                    _3d_width_length = _3d_object_info["width_length_summary"]
                        
                    _3d_brightness = (_3d_object_info["brightness_summary"][3]) 
                    _3d_brightness_std = (_3d_object_info["brightness_summary"][-1]) 

                    #print(_3d_object[key])

                    
                                    #Area based similiarity
                    _2d_area_image_1 = self.comparator.get_2d_picture_area(_2d_image_path_image_1)
                    _2d_area_image_2 = self.comparator.get_2d_picture_area(_2d_image_path_image_2)    
                    #Brightness based simliarity
                    _2d_brightness_summary_2 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_2)
                    _2d_brightness_summary_1 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_1)
                    
                    _2d_brightness_1 = _2d_brightness_summary_1[3]
                    _2d_brightness_2 = _2d_brightness_summary_2[3]

                    _2d_brightness_std_1 = _2d_brightness_summary_1[-1]
                    _2d_brightness_std_2 = _2d_brightness_summary_2[-1]


                    #Let's do the third one: color based similarity
                    #Prepare the colors summaries for these two pictures
                    #Not that useful we found out.
                    front_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_1))
                    back_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_2))  
                    

                    _2d_width_length_1 = (self.comparator.get_2d_width_length(_2d_image_path_image_1))
                    _2d_width_length_2 = (self.comparator.get_2d_width_length(_2d_image_path_image_2)) 
                    
                    _3d_width = _3d_width_length[0]
                    _3d_length = _3d_width_length[1]
                    _2d_width_1 = _2d_width_length_1[0]
                    _2d_width_2 = _2d_width_length_2[0]
                    _2d_length_1 = _2d_width_length_1[1]
                    _2d_length_2 = _2d_width_length_2[1]


                    #Fourth one, width length

                    #Here we need to get what the x, y pairs  we want to optimise
                    #1. 3d_area and _2d_area(only the closer one)
                    #2. 3d_brightness and _2d_brigtheness(only the closer one)
                    #3. 3d_brightess_std and _2d_brigthness_std(only the closer one)
                    #4. 3d_length, 3d_width, 2d_length, 2d_width(only the closer one)

                    #1. area data
                    current_match = {}
                    current_match["_3d_area"] = _3d_area
                    if(self.get_similarity_two_nums(_3d_area, _2d_area_image_1 ) >  self.get_similarity_two_nums(_3d_area, _2d_area_image_2 ) ): 
                        current_match["_2d_area"] = _2d_area_image_2
                    else: 
                        current_match["_2d_area"] = _2d_area_image_1
                    
                    #2 brightness data
                    current_match["_3d_brightness"] = _3d_brightness      
                    if(self.get_similarity_two_nums(_3d_brightness, _2d_brightness_1 ) >  self.get_similarity_two_nums(_3d_brightness, _2d_brightness_2 ) ): 
                        current_match["_2d_brightness"] = _2d_brightness_2
                    else: 
                        current_match["_2d_brightness"] = _2d_brightness_1                    
                    #3 brightness std data
                    current_match["_3d_brightness_std"] = _3d_brightness_std      
                    if(self.get_similarity_two_nums(_3d_brightness_std, _2d_brightness_std_1 ) >  self.get_similarity_two_nums(_3d_brightness_std, _2d_brightness_std_2 ) ): 
                        current_match["_2d_brightness_std"] = _2d_brightness_std_2
                    else: 
                        current_match["_2d_brightness_std"] = _2d_brightness_std_1                    

                    #4    
                    # 
                    current_match["_3d_width"] = _3d_width                              
                    current_match["_3d_length"] = _3d_length                          
                    unadjusted_similarity_1  = (self.get_similarity_two_nums(_2d_length_1, _3d_length ) +  self.get_similarity_two_nums( _2d_width_1, _3d_width ))/2
                    unadjusted_similarity_2  = (self.get_similarity_two_nums(_2d_length_2, _3d_length ) +  self.get_similarity_two_nums(_2d_width_2, _3d_width))/2
                    if(unadjusted_similarity_1 > unadjusted_similarity_2):
                        current_match["_2d_width"] = _2d_width_2                              
                        current_match["_2d_length"] = _2d_length_2         
                    else:
                        current_match["_2d_width"] = _2d_width_1                             
                        current_match["_2d_length"] = _2d_length_1         
                        

                    for_ml["data"].append({"current_match": current_match, "path": str(res)})

 
                    print(_2d_image_path_image_1)
                    print(_2d_image_path_image_2)
                    print()
        simple_save_json(for_ml, "./for_ml.json")
        print(f"Timed passed: {time.time() - current} seconds")
        #('N', 38, 478130, 4419430, 128, 74, 'pottery', 'body', None, '2b2e382f-b307-4bb5-a01b-23618b47573b', 2022, 19, 7, False)





    def testing_images_bounding_circcle(self):
  
        sherds = (get_all_pottery_sherd_info())
        non_sherds = [x for x in sherds if x[12]!= None and x[13]!=None]
        to_be_saved = {}
        to_be_saved["data"] = []
        _3d_object ={}

        for data in self.json_data["past_records"]:
            key =  f'{data["utm_easting"]}-{data["utm_northing"]}-{data["hemisphere"]}-{data["zone"]}-{data["context"]}-{int(data["batch_num"])}-{data["piece_num"]}'  
           
            _3d_object[key] = data
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
                print()
                print(_2d_image_path_image_1)
                print(_2d_image_path_image_1)
                print(self.get_enclosing_circle_area(_2d_image_path_image_1, self.comparator.ceremicPredictor))
                print(self.get_area_by_pixels(_2d_image_path_image_1, self.comparator.ceremicPredictor))
                print(self.get_enclosing_circle_area(_2d_image_path_image_2, self.comparator.ceremicPredictor))
                print(self.get_area_by_pixels(_2d_image_path_image_2, self.comparator.ceremicPredictor))
    def adjusting_similaritiy_weights(self):

        current = time.time()

        to_be_saved = {}
        to_be_saved["data"] = []
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
                    _3d_width_length = _3d_object_info["width_length_summary"]
                        
                    _3d_brightness = (_3d_object_info["brightness_summary"][3]) 
                    _3d_brightness_std = (_3d_object_info["brightness_summary"][-1]) 

                    #print(_3d_object[key])

                    
                                    #Area based similiarity
                    _2d_area_1 = self.comparator.get_2d_picture_area(_2d_image_path_image_1)
                    _2d_area_2 = self.comparator.get_2d_picture_area(_2d_image_path_image_2)    
                    #Brightness based simliarity
                    _2d_brightness_summary_2 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_2)
                    _2d_brightness_summary_1 = self.comparator.get_brightness_summary_from_2d(_2d_image_path_image_1)
                    
                    _2d_brightness_1 = _2d_brightness_summary_1[3]
                    _2d_brightness_2 = _2d_brightness_summary_2[3]

                    _2d_brightness_std_1 = _2d_brightness_summary_1[-1]
                    _2d_brightness_std_2 = _2d_brightness_summary_2[-1]


                    #Let's do the third one: color based similarity
                    #Prepare the colors summaries for these two pictures
                    #Not that useful we found out.
                    front_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_1))
                    back_color = (self.comparator.get_color_summary_from_2d(_2d_image_path_image_2))  
                    

                    _2d_width_length_1 = (self.comparator.get_2d_width_length(_2d_image_path_image_1))
                    _2d_width_length_2 = (self.comparator.get_2d_width_length(_2d_image_path_image_2)) 
                    
                    _3d_width = _3d_width_length[0]
                    _3d_length = _3d_width_length[1]
                    _2d_width_1 = _2d_width_length_1[0]
                    _2d_width_2 = _2d_width_length_2[0]
                    _2d_length_1 = _2d_width_length_1[1]
                    _2d_length_2 = _2d_width_length_2[1]

                    parameters = self.parameters
                    area_similarity = self.get_area_similarity(_3d_area, _2d_area_1, _2d_area_2,parameters["area"]["slope"], parameters["area"]["intercept"])
                    brightness_similarity = self.get_brightness_similarity(_3d_brightness, _2d_brightness_1, _2d_brightness_2,parameters["brightness"]["slope"], parameters["brightness"]["intercept"])
                    brightness_std_similarity = self.get_brightness_std_similarity(_3d_brightness_std, _2d_brightness_std_1, _2d_brightness_std_2,parameters["brightness_std"]["slope"], parameters["brightness_std"]["intercept"])
                    width_length_similarity = self.get_width_length_similarity(_3d_width, _3d_length, _2d_width_1,  _2d_width_2, _2d_length_1, _2d_length_2,parameters["width"]["slope"], parameters["width"]["intercept"],parameters["length"]["slope"], parameters["length"]["intercept"])
                    
                    similarities = {
                        "area_similarity": area_similarity,
                        "brightness_similarity": brightness_similarity,
                        "brightness_std_similarity": brightness_std_similarity,
                        "width_length_similarity": width_length_similarity,
                        "target": 1
                    }
                    to_be_saved["data"].append({"current_match": similarities, "path": str(res)})
                    print(similarities)
                    print(str(res))
        
        simple_save_json(to_be_saved, "weights.json") 
        print(f"Timed passed: {time.time() - current} seconds")
            