from presenter.mixins.choose_directory.main_choose_directory import ChooseDirectoryMixin
from presenter.mixins.load_data.main_load_jpgs_plys import LoadDataMixin
from presenter.mixins.match.add_and_remove_match import AddAndRemoveMatchMixin
from presenter.mixins.load_data.load_1_jpg_pair import Load1jpgPairMixin
from presenter.mixins.display_3d_model import Display3dModelMixin
from presenter.mixins.calculuate_similarity.get_3d_models_sorted_by_similarity import get3dModelSortedBySimilarityMixin
from presenter.mixins.calculuate_similarity.calculuate_individual_similarities import CalculateIndividualSimilaritiesMixin

from presenter.mixins.measure_pixels_data.main_measure_pixels_data import MeasurePixelsDataMixin
from presenter.mixins.filters.finds_and_objects_filter import FindsAndObjectsFilter
import time
import re
from pathlib import PurePath
from PyQt5.QtGui import (
    QFont
)
class Mainpresenter(
    ChooseDirectoryMixin,
    MeasurePixelsDataMixin,
    get3dModelSortedBySimilarityMixin,
    CalculateIndividualSimilaritiesMixin,
    Load1jpgPairMixin,
    LoadDataMixin,
    AddAndRemoveMatchMixin,
    Display3dModelMixin,
    FindsAndObjectsFilter
):



    def __init__(self, model, view):
        main_presenter = self
        self.main_model = model
        self.main_view = view

        self.main_model.prepare_data(self.main_view)
        
        self.main_view.set_up_view_presenter_connection(main_presenter)
        self.populate_hemispheres()
        view.contextDisplay.setText(main_presenter.get_context_string())
     
        super().__init__()

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self
