from controller.mixins.select_path import SelectPathMixin
from controller.mixins.load_jpgs_plys import LoadJpgsPlysMixin
from controller.mixins.add_and_remove_match import AddAndRemoveMatchMixin
from controller.mixins.load_1_jpg_pair import Load1jpgPairMixin
from controller.mixins.display_3d_model import Display3dModelMixin
from controller.mixins.calculuate_similarity import CalculateSimilarityMixin
from controller.mixins.measure_pixels_data import MeasurePixelsDataMixin


class MainController(
    SelectPathMixin,
    MeasurePixelsDataMixin,
    CalculateSimilarityMixin,
    Load1jpgPairMixin,
    LoadJpgsPlysMixin,
    AddAndRemoveMatchMixin,
    Display3dModelMixin,
):

    # 1) bridging the view(gui) and the model(data) when events(such as mouse click) happen

    # 2) calculation and application logic

    def __init__(self,  model, view):

        self.main_model= model
        self.main_view = view
        self.main_model.prepare_data(self.main_view)
        MeasurePixelsDataMixin.__init__(self, self.main_view, self.main_model)


        main_controller = self
        self.populate_hemispheres()
        self.main_view.set_up_view_controller_connection(main_controller)
        
        view.contextDisplay.setText(main_controller.get_context_string())
        
        super().__init__(self.main_view, self.main_model)

    def get_model_view_controller(self):

        return self.main_model, self.main_view, self
