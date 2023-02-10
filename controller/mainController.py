from controller.selectPathControllerMixin import SelectPathControllerMixin
from controller.loadJpgsPlysControllerMixin import LoadJpgsPlysControllerMixin
from controller.addAndRemoveMatchControllerMixin import AddAndRemoveMatchControllerMixin
from controller.load1jpgPairController import Load1jpgPairController
from controller.display3dModelControllerMixin import Display3dModelControllerMixin
from controller.calculuateSimilarityControllerMixin import CalculateSimilarityControllerMixin
from controller.measurePixelsDataControllerMixin import MeasurePixelsDataControllerMixin
class MainController( SelectPathControllerMixin, MeasurePixelsDataControllerMixin, CalculateSimilarityControllerMixin, Load1jpgPairController,LoadJpgsPlysControllerMixin, AddAndRemoveMatchControllerMixin,  Display3dModelControllerMixin):
     #1) bridging the view(gui) and the model(data) when events(such as mouse click) happen
     #2) calculation and application logic
     
    def __init__(self, view, model):
        self.mainModel = model
        self.mainView = view 
        MeasurePixelsDataControllerMixin.__init__(self, self.mainView ,      self.mainModel)
        super(  ).__init__(self.mainView ,      self.mainModel)

    def get_model_view_controller(self):
        return self.mainModel, self.mainView, self

