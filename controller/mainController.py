from controller.selectPathControllerMixin import SelectPathControllerMixin


class MainController(SelectPathControllerMixin): #bridging the view(gui) and the model(data)
    def __init__(self, view):
        super(MainController, self).__init__(view)

    