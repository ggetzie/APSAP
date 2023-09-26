from presenter.mixins.choose_directory.main_choose_directory import ChooseDirectoryMixin
from presenter.mixins.load_data.main_load_data import LoadDataMixin
from presenter.mixins.match.add_and_remove_match import AddAndRemoveMatchMixin

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
    LoadDataMixin,
    AddAndRemoveMatchMixin,
    FindsAndObjectsFilter
):

    """This main_presenter inherits all the mixins' methods to handle the interactive behaviours of the applications,
    such that when you click on a button or choose an item in a select, things change in the application. 
    """    

    def __init__(self, model, view):
        main_presenter = self

        # Bind both the model and view into the presenter
        self.main_model = model
        self.main_view = view

        # Loading all the initial data of configuration
        self.main_model.prepare_data(self.main_view)
        
        # Setting up the connections between the presenters' methods and the buttons, selects and other gui elements in the 
        #view
        self.main_view.set_up_view_presenter_connection(main_presenter)
        
        #Loading the first context
        self.populate_hemispheres()
        view.contextDisplay.setText(main_presenter.get_context_string())
     
        super().__init__()

    def get_model_view_presenter(self):

        return self.main_model, self.main_view, self
