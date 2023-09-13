from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
from presenter.mixins.calculuate_similarity.calculuate_individual_similarities import (
    CalculateIndividualSimilaritiesMixin,
)
from glob import glob as glob
import re
import time
from pathlib import Path as Path


class CalculateSimilarityMixin(
    CalculateIndividualSimilaritiesMixin
):  # bridging the view(gui) and the model(data)
    def genereate_similiarity_ranked_pieces(self, similarities_list):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        grand_similarity = []

        for similairty, batch_num, piece_num, year in similarities_list:
            
         
            weighted_mean = (
                 similairty["area_similarity"]  * 1.2
                #  + similairty["brightness_similarity"] * 0.3   Not usable at this stage
                #  + similairty["brightness_std_similarity"] * 0.1
                  + similairty["width_length_similarity"] * 0.2
             
                 + similairty["contour_simlarity"] * 0.7
            )

            grand_similarity.append([weighted_mean, batch_num, piece_num, year])
        return grand_similarity

    def get_batch_details(self):
        """
        This function gets how many items are in each batches
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        all_model_paths = glob(
            str(
                main_presenter.get_context_dir()
                / main_model.path_variables["MODELS_FILES_DIR"]
            )
        )

        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"], path.replace("\\", "/")
            )
            # This error happens when the relative path is different
            print(m.group(1))
            batch_num = int(m.group(2))
            if batch_num not in batches_dict:
                batches_dict[batch_num] = 0
            else:
                batches_dict[batch_num] += 1
        return batches_dict

    def get_contour_2d(self, img_path):
        import numpy as np
        import open3d as o3d
        from PIL import Image
        import cv2

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        image = Image.open(img_path).resize((450, 300), Image.ANTIALIAS)

        masked_ceremics = main_presenter.ceremic_predictor.predict(image)

        masked_ravel = np.array(masked_ceremics)
        masked_ravel[masked_ravel < 180] = 0

        masked_ravel[masked_ravel != 0] = 255

        pil_image = Image.fromarray(masked_ravel).convert("RGB")

        open_cv_image = np.array(pil_image)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(img_gray, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, 2, 1)
        cnt2 = contours[0]
        return cnt2

    def get_similaritiy_scores(self, image_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        img_1_path = image_path / "1.jpg"
        img_2_path = image_path / "2.jpg"

 
        (
            area_img_1,
            area_img_2,
            light_ima_1,
            light_ima_2,
            img_1_width_length,
            img_2_width_length,
        ) = self.measure_pixels_2d(img_1_path, img_2_path)
        similarity_scores = []

        import cv2
    
        contour1_2d = self.get_contour_2d(img_1_path)
        contour2_2d = self.get_contour_2d(img_2_path)
        batch_details = self.get_batch_details()

        # Getting all 3d models from the image paths and get them
        from glob import glob

        all_3d_models_paths = glob(
            str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
        )
      

        for path_3d in all_3d_models_paths:
            (
                    _3d_area,
                    width_length_3d,
                    color_brightness_3d,
                    color_brightness_std_3d,
                    contour_3d,
                    batch_num,
                    piece_num,
                    year
            )= self.measure_pixels_3d(path_3d)
            
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
                contour1_2d,
                contour2_2d,
                contour_3d,
            )
            similarity_scores.append(
                [similairty, batch_num, piece_num, year]
            )  # _#similairty, batch_num, piece_num])

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
        contour1_2d,
        contour2_2d,
        contour_3d,
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

        contour_simlarity = main_presenter.get_contour_simlarity(
            contour1_2d, contour2_2d, contour_3d
        )

        similarities = {
            "area_similarity": area_similarity,
            "brightness_similarity": brightness_similarity,
            "brightness_std_similarity": brightness_std_similarity,
            "width_length_similarity": width_length_similarity,
            "contour_simlarity": contour_simlarity,
        }
        return similarities
