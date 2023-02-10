from controller.selectPathControllerMixin import SelectPathControllerMixin
from controller.loadJpgsPlysControllerMixin import LoadJpgsPlysControllerMixin
from controller.addAndRemoveMatchControllerMixin import AddAndRemoveMatchControllerMixin
from controller.load1jpgPairController import Load1jpgPairController
from controller.display3dModelControllerMixin import Display3dModelControllerMixin

class MainController(SelectPathControllerMixin, LoadJpgsPlysControllerMixin, AddAndRemoveMatchControllerMixin, Load1jpgPairController, Display3dModelControllerMixin):
     #bridging the view(gui) and the model(data)

     
    def __init__(self, view, model):
        self.mainModel = model
        self.mainView = view 
        super(MainController, self).__init__(self.mainView ,      self.mainModel)

    def get_model_view_controller(self):
        return self.mainModel, self.mainView, self

