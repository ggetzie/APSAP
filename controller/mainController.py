from controller.selectPathControllerMixin import SelectPathControllerMixin
from controller.TempMixin import TempMixin

class MainController(SelectPathControllerMixin, TempMixin): #bridging the view(gui) and the model(data)
    def __init__(self, view, model):
        self.mainModel = model
        self.mainView = view 
        super(MainController, self).__init__(self.mainView ,      self.mainModel)

 
   
 
    def get_model_view_controller(self):
        return self.mainModel, self.mainView, self

