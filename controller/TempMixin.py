
import time
from PyQt5.QtGui import (

    QStandardItemModel,
)
class TempMixin: #bridging the view(gui) and the model(data)

    def __init__(self, view, model):
        #Notice this object is the controller, that which connects the view(GUI) and the model(data)
        controller = self

        view.contextDisplay.setText(controller.get_context_string())


    def contextChanged(self):
        model, view, controller = self.get_model_view_controller()

        view.statusLabel.setText(f"")
        view.selected_find.setText(f"")
        view.current_batch.setText(f"")
        view.current_piece.setText(f"")
        view.new_batch.setText(f"")
        view.new_piece.setText(f"")
        #self.contextDisplay.setText(self.get_context_string())
        if hasattr(view, "current_pcd"):
            view.vis.remove_geometry(view.current_pcd)
            view.current_pcd = None

        model = QStandardItemModel(view)
        view.sortedModelList.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", view.populate_finds],
            ["Loading models. It might take a while", view.populate_models],
        ]

        now = time.time()
        view.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")