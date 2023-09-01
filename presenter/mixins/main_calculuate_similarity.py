from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
from presenter.mixins.calculuate_similarity.calculuate_individual_similarities import CalculateIndividualSimilaritiesMixin
from glob import glob as glob
import re
import time
from pathlib import Path as Path
class CalculateSimilarityMixin(CalculateIndividualSimilaritiesMixin):  # bridging the view(gui) and the model(data)


    def genereate_similiarity_ranked_pieces(self, similarities_list):
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        grand_similarity = []
        
        for _threeple in similarities_list:
            vals = _threeple[0]
            main_view.weights = main_view.get_features_weights()
            weighted_mean =  (vals["area_similarity"] * main_view.weights["area_similarity"] +  
                            vals["brightness_similarity"] * main_view.weights["brightness_similarity"]  +  
                            vals["brightness_std_similarity"] * main_view.weights["brightness_std_similarity"]  + 
                             vals["width_length_similarity"] * main_view.weights["width_length_similarity"]+  
                            
                         +  vals["extra_similarities"] * main_view.weights["extra_similarities"] 
                            )

            grand_similarity.append(
                # [[ weighted_mean ], _threeple[1], _threeple[2]]
                 [[ _threeple[-1]] + 2 * vals["brightness_similarity"] , _threeple[1], _threeple[2]]
            )
        return grand_similarity

    def get_batch_details(self):
        """
            This function gets how many items are in each batches
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()    
        all_model_paths = glob(str(main_presenter.get_context_dir() / main_model.path_variables["MODELS_FILES_DIR"]))
      

        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"], path.replace("\\", "/")
            )
            # This error happens when the relative path is different
            batch_num = int(m.group(1))
            if batch_num not in batches_dict:
                batches_dict[batch_num] = 0 
            else:
                batches_dict[batch_num] += 1
        return batches_dict

    def get_ply_identifier(self, batch_num, piece_num, batch_details):
        
        maximum = max(batch_details.keys())
        minimum = min(batch_details.keys())
        identifier = 0
        for i in range(minimum, int(batch_num)):
            if i in batch_details:
                identifier += batch_details[i]
        identifier += int(piece_num)
        return identifier
 
    # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(img_gray, 127, 255,0)
        contours, hierarchy  = cv2.findContours(thresh,2,1)
        cnt1 = contours[0]
        ply_window.remove_geometry(current_pcd_load)
        del ctr
        return cnt1

    
    
    def get_contour_2d (self, img_path):

        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2
        main_model, main_view, main_presenter = self.get_model_view_presenter()    

        image =   Image.open(img_path).resize((450, 300), Image.ANTIALIAS)  

        masked_ceremics = main_presenter.ceremic_predictor.predict(image)
    
        masked_ravel = (((np.array(masked_ceremics) )))
        masked_ravel[masked_ravel<180] = 0
        
        
        masked_ravel[masked_ravel!=0] = 255
    
        pil_image = Image.fromarray(masked_ravel).convert("RGB")
      
        open_cv_image = np.array(pil_image) 
    # Convert RGB to BGR 
        open_cv_image = open_cv_image[:, :, ::-1].copy() 
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
        
        ret, thresh = cv2.threshold(img_gray, 127, 255,0)
        contours, hierarchy  = cv2.findContours(thresh,2,1)
        cnt2 = contours[0]
        return cnt2
    








    def get_similaritiy_scores(self,  image_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        img_1_path = image_path / "1.jpg"
        img_2_path = image_path / "2.jpg"

        img_1_data = (main_model.get_img1_data_from_sqlite(img_1_path))
        img_2_data = (main_model.get_img2_data_from_sqlite(img_2_path))
        if img_1_data and img_2_data:
            area_img_1, light_ima_1, img_1_width_length = img_1_data
            area_img_2, light_ima_2, img_2_width_length = img_2_data
            print("We get the data from db")
         

        # if str(img_1_path) in main_model.path_info_dict and str(img_2_path) in main_model.path_info_dict:
        #     print("Getting the jpg data from cache, skip calculating")
        #     obj_img_1 =  main_model.path_info_dict[str(img_1_path)]
        #     obj_img_2 =  main_model.path_info_dict[str(img_2_path)]
        #     area_img_1 = obj_img_1["area_img_1"]
        #     light_ima_1 = obj_img_1["light_ima_1"]
        #     img_1_width_length = obj_img_1["img_1_width_length"]
        #     area_img_2 = obj_img_2["area_img_2"]
        #     light_ima_2 = obj_img_2["light_ima_2"]
        #     img_2_width_length = obj_img_2["img_2_width_length"]   
        else:
            print("Calculuate the jpg data")
            area_img_1,  area_img_2, light_ima_1, light_ima_2, img_1_width_length, img_2_width_length= self.measure_pixels_2d(img_1_path, img_2_path)
        similarity_scores = []
        
        img_identifier =  (int(Path(image_path).parts[-2]) - 1)
 
        import cv2

        ct1 = (self.get_contour_2d(img_1_path))
        ct2 = (self.get_contour_2d(img_2_path))
        batch_details = self.get_batch_details()
        for i in range(len(main_view.areas_3d)):
            _3d_area,  all_3d_area_circle_ratio, width_length_3d, color_brightness_3d, color_brightness_std_3d, batch_num, piece_num, contour = self.measure_pixels_3d(i)

            ply_identifier =  self.get_ply_identifier(batch_num, piece_num, batch_details )
            # model_3d_path = (str(main_presenter.get_context_dir() / main_model.path_variables["MODELS_FILES_DIR"]).replace("*", f"{int(batch_num):03}", 1).replace(
            #     "*", f"{int(piece_num)}", 1
            # ))
     
            ct_3d = contour
            ret1 = cv2.matchShapes(ct1,ct_3d,1,0.0)
            ret2 = cv2.matchShapes(ct2,ct_3d,1,0.0)
            sim = min(ret1, ret2)
            
            similairty = main_presenter.get_similarity(
                _3d_area,
                area_img_1,
                area_img_2,
                color_brightness_3d,
                light_ima_1[3],
                light_ima_2[3],
                color_brightness_std_3d,
                light_ima_1[-1],
                light_ima_2[-1],
                width_length_3d[0],
                width_length_3d[1],
                img_1_width_length[0],
                img_1_width_length[1],
                img_2_width_length[0],
                img_2_width_length[1],

                img_identifier,
                ply_identifier
            )
            similarity_scores.append([similairty, batch_num, piece_num,  sim])#_#similairty, batch_num, piece_num])
       
        return similarity_scores



    def get_similarity(
        self,
        _3d_area,
        _2d_area_1,
        _2d_area_2,
        _3d_brightness,
        _2d_brightness_1,
        _2d_brightness_2,
        _3d_brightness_std,
        _2d_brightness_std_1,
        _2d_brightness_std_2,
        _3d_pic_side_1,
        _3d_pic_side_2,
        _first_pic_side_1,
        _first_pic_side_2,
        _second_pic_side_1,
        _second_pic_side_2,
 
        img_identifier,
        ply_identifier
    ):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
  
        parameters = main_model.parameters
         
        area_similarity = main_presenter.get_area_similarity(
            _3d_area,
            _2d_area_1,
            _2d_area_2,
            parameters["area"]["slope"],
            parameters["area"]["intercept"],
        )
        brightness_similarity = main_presenter.get_brightness_similarity(
            _3d_brightness,
            _2d_brightness_1,
            _2d_brightness_2,
            parameters["brightness"]["slope"],
            parameters["brightness"]["intercept"],
        )
        brightness_std_similarity = main_presenter.get_brightness_std_similarity(
            _3d_brightness_std,
            _2d_brightness_std_1,
            _2d_brightness_std_2,
            parameters["brightness_std"]["slope"],
            parameters["brightness_std"]["intercept"],
        )
        width_length_similarity = main_presenter.get_width_length_similarity(
            _3d_pic_side_1,
            _3d_pic_side_2,
            _first_pic_side_1,
            _first_pic_side_2,
            _second_pic_side_1,
            _second_pic_side_2,
            parameters["width"]["slope"],
            parameters["width"]["intercept"],
            parameters["length"]["slope"],
            parameters["length"]["intercept"],
        )
 
        extra_similarities = main_presenter.get_similarity_two_nums(img_identifier, ply_identifier)

        similarities = {
                "area_similarity": area_similarity,
                "brightness_similarity": brightness_similarity,
                "brightness_std_similarity": brightness_std_similarity,
                "width_length_similarity": width_length_similarity,
             
                "extra_similarities": extra_similarities
        } 
        return similarities
   
