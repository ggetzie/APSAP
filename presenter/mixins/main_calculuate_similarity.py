from PIL.ImageQt import ImageQt
from scipy.stats import gmean, tmean
import numpy as np
from presenter.mixins.calculuate_similarity.calculuate_individual_similarities import CalculateIndividualSimilaritiesMixin

class CalculateSimilarityMixin(CalculateIndividualSimilaritiesMixin):  # bridging the view(gui) and the model(data)


    def genereate_similiarity_ranked_pieces(self, similarities_list):

        grand_similarity = []
        for _threeple in similarities_list:
            vals = _threeple[0]
            grand_similarity.append(
                [[gmean(vals) + tmean(vals)], _threeple[1], _threeple[2]]
            )
        return grand_similarity

    def get_similaritiy_scores(self, index, image_path):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        _2d_image_path_image_1 = image_path / "1.jpg"
        _2d_image_path_image_2 = image_path / "2.jpg"

        _2d_area_image_1,  _2d_area_image_2, color_brightness_2d_image_1, color_brightness_2d_image_2, _2d_width_length_image_1, _2d_width_length_image_2, _2d_area_circle_ratio_image_1,  _2d_area_circle_ratio_image_2 = self.get_pixels_measuring_results__2d(_2d_image_path_image_1, _2d_image_path_image_2)

        similarity_scores = []

        for i in range(len(main_view.all_3d_areas)):
            _3d_area, _3d_color, all_3d_area_circle_ratio, width_length_3d, color_brightness_3d, color_brightness_std_3d, batch_num, piece_num = self.get_pixels_measuring_results__3d(i)
           
            similairty = main_presenter.get_similarity(
                _3d_area,
                _2d_area_image_1,
                _2d_area_image_2,
                color_brightness_3d,
                color_brightness_2d_image_1[3],
                color_brightness_2d_image_2[3],
                color_brightness_std_3d,
                color_brightness_2d_image_1[-1],
                color_brightness_2d_image_2[-1],
                width_length_3d[0],
                width_length_3d[1],
                _2d_width_length_image_1[0],
                _2d_width_length_image_1[1],
                _2d_width_length_image_2[0],
                _2d_width_length_image_2[1],
                _2d_area_circle_ratio_image_1,
                _2d_area_circle_ratio_image_2,
                all_3d_area_circle_ratio,
            )
            # similarity_scores.append([self.get_3d_2d_simi(color_brightness_3d, color_brightness_std_3d, _3d_area, _2d_area_image_2, _2d_area_image_1, color_brightness_2d_image_2, color_brightness_2d_image_1, front_color, back_color, _3d_color, width_length_3d, _2d_width_length_image_1, _2d_width_length_image_2  ), batch_num, piece_num])
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
        _2d_area_circle_ratio_image_1,
        _2d_area_circle_ratio_image_2,
        all_3d_area_circle_ratio,
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
        area_circle_similarity = main_presenter.get_area_circle_similarity(
            _2d_area_circle_ratio_image_1,
            _2d_area_circle_ratio_image_2,
            all_3d_area_circle_ratio,
            0.9055558282782922,
            0.03996414943733839,
        )
        total_similarity = (
            area_similarity
            + brightness_similarity
            + brightness_std_similarity
            + width_length_similarity
        )
        # weights = np.array([0.4, 0.38, 0.12, 0.1])
        # weights = np.array([2.85877858e-01 ,7.14122142e-01 ,0.00000000e+00, 5.55111512e-17, 0.1])
        similarities = np.array(
            [
                area_similarity,
                brightness_similarity,
                brightness_std_similarity,
                width_length_similarity,
                area_circle_similarity,
            ]
        )
        # return np.dot(weights, similarities)# total_similarity/4
        return similarities
        # return area_circle_similarity

