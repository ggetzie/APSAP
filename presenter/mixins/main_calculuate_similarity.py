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
        print(main_view.weights)
        for _threeple in similarities_list:
            vals = _threeple[0]
 
            weighted_mean =  (vals["area_similarity"] * main_view.weights["area_similarity"] +  
                            vals["brightness_similarity"] * main_view.weights["brightness_similarity"]  +  
                            vals["brightness_std_similarity"] * main_view.weights["brightness_std_similarity"]  + 
                             vals["width_length_similarity"] * main_view.weights["width_length_similarity"]+  
                            
                         +  vals["extra_similarities"] * main_view.weights["extra_similarities"] 
                            )

            grand_similarity.append(
                [[ weighted_mean], _threeple[1], _threeple[2]]
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
        

    def get_similaritiy_scores(self,  image_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        img_1_path = image_path / "1.jpg"
        img_2_path = image_path / "2.jpg"
        area_img_1,  area_img_2, light_ima_1, light_ima_2, img_1_width_length, img_2_width_length= self.measure_pixels_2d(img_1_path, img_2_path)
        similarity_scores = []
        
        img_identifier =  (int(Path(image_path).parts[-2]) - 1)
      
        batch_details = self.get_batch_details()
        for i in range(len(main_view.areas_3d)):
            _3d_area,  all_3d_area_circle_ratio, width_length_3d, color_brightness_3d, color_brightness_std_3d, batch_num, piece_num = self.measure_pixels_3d(i)

            ply_identifier =  self.get_ply_identifier(batch_num, piece_num, batch_details )

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
            similarity_scores.append([similairty, batch_num, piece_num])
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
   
