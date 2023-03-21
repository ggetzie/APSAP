from presenter.mixins.select_path import SelectPathMixin
from presenter.mixins.main_load_jpgs_plys import LoadJpgsPlysMixin
from presenter.mixins.add_and_remove_match import AddAndRemoveMatchMixin
from presenter.mixins.load_1_jpg_pair import Load1jpgPairMixin
from presenter.mixins.display_3d_model import Display3dModelMixin
from presenter.mixins.main_calculuate_similarity import CalculateSimilarityMixin
from presenter.mixins.main_measure_pixels_data import MeasurePixelsDataMixin
import time
import re
from pathlib import PurePath
class Mainpresenter(
    SelectPathMixin,
    MeasurePixelsDataMixin,
    CalculateSimilarityMixin,
    Load1jpgPairMixin,
    LoadJpgsPlysMixin,
    AddAndRemoveMatchMixin,
    Display3dModelMixin,
):



    def __init__(self, model, view):

        self.main_model = model
        self.main_view = view
        main_presenter = self
        
        self.main_model.prepare_data(self.main_view)
        
        self.main_view.set_up_view_presenter_connection(main_presenter)
        self.populate_hemispheres()
        view.contextDisplay.setText(main_presenter.get_context_string())

        MeasurePixelsDataMixin.__init__(self, self.main_view, self.main_model)
       
        super().__init__(self.main_view, self.main_model)

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self
