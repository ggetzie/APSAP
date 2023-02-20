import pathlib
import json
import time
from  computation.nn_segmentation import MaskPredictor
ceremic_predictor =  MaskPredictor("./computation/ceremicsmask.pt")
from scipy.ndimage import binary_dilation

class DebugFuncs():

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
                img_1_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "1.jpg"
                img_2_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "2.jpg"
                if pathlib.Path(img_1_path).is_file() and pathlib.Path(img_2_path).is_file():

                    
                    
                    _3d_object_info = _3d_object[key]
                    _3d_area = _3d_object_info["area"]
    
                    _3d_color = _3d_object_info["colors_summary"]
                    _3d_width_length = _3d_object_info["width_length_summary"]
                        
                    _3d_brightness = (_3d_object_info["brightness_summary"][3]) 
                    _3d_brightness_std = (_3d_object_info["brightness_summary"][-1]) 

                    #print(_3d_object[key])

                    
                                    #Area based similiarity
                    area_img_1 = self.comparator.get_2d_area(img_1_path)
                    area_img_2 = self.comparator.get_2d_area(img_2_path)    
                    #Brightness based simliarity
                    _2d_brightness_summary_2 = self.comparator.get_2d_light_summary(img_2_path)
                    _2d_brightness_summary_1 = self.comparator.get_2d_light_summary(img_1_path)
                    
                    _2d_brightness_1 = _2d_brightness_summary_1[3]
                    _2d_brightness_2 = _2d_brightness_summary_2[3]

                    _2d_brightness_std_1 = _2d_brightness_summary_1[-1]
                    _2d_brightness_std_2 = _2d_brightness_summary_2[-1]


                    #Let's do the third one: color based similarity
                    #Prepare the colors summaries for these two pictures
                    #Not that useful we found out.
                    front_color = (self.comparator.get_color_summary_from_2d(img_1_path))
                    back_color = (self.comparator.get_color_summary_from_2d(img_2_path))  
                    

                    _2d_width_length_1 = (self.comparator.get_2d_width_length(img_1_path))
                    _2d_width_length_2 = (self.comparator.get_2d_width_length(img_2_path)) 
                    
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
                    if(self.get_similarity_two_nums(_3d_area, area_img_1 ) >  self.get_similarity_two_nums(_3d_area, area_img_2 ) ): 
                        current_match["_2d_area"] = area_img_2
                    else: 
                        current_match["_2d_area"] = area_img_1
                    
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

 
                    print(img_1_path)
                    print(img_2_path)
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
        count  = 0

        area_circle_data = { "data": []}
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
                #print(f"key: {key}")
                #print(f"i: {i}")
                res = ( self.file_root/ str(i[0])/ str(i[1])/  str(i[2])/ str(i[3])/  str(i[4]))
                _2d_pic_id = i[5]
                img_1_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "1.jpg"
                img_2_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "2.jpg"
                batch = i[11]
                piece = i[12]
                path =  (str((res/MODELS_FILES_DIR)))
                _3d_model_path = (path.replace("*", f"{int(batch):03}", 1).replace("*", f"{int(piece)}", 1)) 
                if pathlib.Path(img_1_path).is_file() and pathlib.Path(img_2_path).is_file() and pathlib.Path(_3d_model_path).is_file():
                    count += 1
             
                    current_data = {

                    }
                    _2d_pixel_area_1 = self.comparator.get_2d_area_by_pixels(img_1_path, self.comparator.ceremic_predictor)
                    _2d_pixel_area_2 = self.comparator.get_2d_area_by_pixels(img_2_path, self.comparator.ceremic_predictor)
                    _2d_pixel_circle_1 = self.comparator.get_2d_enclosing_circle_area(img_1_path, self.comparator.ceremic_predictor)
                    _2d_pixel_circle_2 = self.comparator.get_2d_enclosing_circle_area(img_2_path, self.comparator.ceremic_predictor)
                    _3d_pixel_area = self.comparator.get_3d_object_area_in_pixels(_3d_model_path )
                    _3d_pixel_circle = self.comparator.get_3d_object_circle_in_pixels(_3d_model_path)
                    _2d_ratio_1 = _2d_pixel_area_1/_2d_pixel_circle_1
                    _2d_ratio_2 = _2d_pixel_area_2/_2d_pixel_circle_2
                    _3d_ratio = _3d_pixel_area/_3d_pixel_circle
                    current_data["_2d_ratio_1"] = _2d_ratio_1
                    current_data["_2d_ratio_2"] = _2d_ratio_2
                    current_data["_3d_ratio"] = _3d_ratio
 
                    print("####################")
                    print(f"_2d_pixel_area_1: {_2d_pixel_area_1}")
                    print(f"_2d_pixel_circle_1: {_2d_pixel_circle_1}")
                    print()
                    print(f"_2d_pixel_area_2: {_2d_pixel_area_2}")
                    print(f"_2d_pixel_circle_2: {_2d_pixel_circle_2}")
                    print()
                    print(f"_3d_pixel_area: {_3d_pixel_area}")
                    print(f"_3d_pixel_circle: {_3d_pixel_circle}")
                    print(f"_2d_ratio_1: {_2d_ratio_1}")
                    print(f"_2d_ratio_2: {_2d_ratio_2}")
                    print(f"_3d_ratio: {_3d_ratio}")

                    print("####################")
                    area_circle_data["data"].append(current_data)

                   # print(_3d_model_path)
           
        simple_save_json(area_circle_data, "./circles.json")
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
                img_1_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "1.jpg"
                img_2_path = res/ FINDS_SUBDIR / str(_2d_pic_id) / FINDS_PHOTO_DIR / "2.jpg"
                if pathlib.Path(img_1_path).is_file() and pathlib.Path(img_2_path).is_file():

                    
                    
                    _3d_object_info = _3d_object[key]
                    _3d_area = _3d_object_info["area"]
    
                    _3d_color = _3d_object_info["colors_summary"]
                    _3d_width_length = _3d_object_info["width_length_summary"]
                        
                    _3d_brightness = (_3d_object_info["brightness_summary"][3]) 
                    _3d_brightness_std = (_3d_object_info["brightness_summary"][-1]) 

                    #print(_3d_object[key])

                    
                                    #Area based similiarity
                    _2d_area_1 = self.comparator.get_2d_area(img_1_path)
                    _2d_area_2 = self.comparator.get_2d_area(img_2_path)    
                    #Brightness based simliarity
                    _2d_brightness_summary_2 = self.comparator.get_2d_light_summary(img_2_path)
                    _2d_brightness_summary_1 = self.comparator.get_2d_light_summary(img_1_path)
                    
                    _2d_brightness_1 = _2d_brightness_summary_1[3]
                    _2d_brightness_2 = _2d_brightness_summary_2[3]

                    _2d_brightness_std_1 = _2d_brightness_summary_1[-1]
                    _2d_brightness_std_2 = _2d_brightness_summary_2[-1]


                    #Let's do the third one: color based similarity
                    #Prepare the colors summaries for these two pictures
                    #Not that useful we found out.
                    front_color = (self.comparator.get_color_summary_from_2d(img_1_path))
                    back_color = (self.comparator.get_color_summary_from_2d(img_2_path))  
                    

                    _2d_width_length_1 = (self.comparator.get_2d_width_length(img_1_path))
                    _2d_width_length_2 = (self.comparator.get_2d_width_length(img_2_path)) 
                    
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
        
        simple_save_json(to_be_saved, "./parameters/data/weights.json") 
        print(f"Timed passed: {time.time() - current} seconds")
            