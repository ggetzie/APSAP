from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import  QMessageBox
from model.database.database_tools import update_match_info

class AddAndRemoveMatchControllerMixin:  # bridging the view(gui) and the model(data)
    
    def __init__(self, view, model):
       
        pass

    def remove_match(self):
        mainModel, view, controller = self.get_model_view_controller()

        # This functions removes the match between the image and the 3d model
        selected_item = view.findsList.currentItem()

        # Only remove model when an image is selected
        if selected_item:
            num = selected_item.text()
            selected_item.setForeground(QColor("black"))
            # Update the database
            (
                easting,
                northing,
                context,
            ) = controller.get_easting_northing_context()
            update_match_info(easting, northing, context, num, None, None)
            # Unred the matched items in the 3d models list
            previous_current_batch_num = view.current_batch.text()
            previous_current_piece_num = view.current_piece.text()

            mod = view.modelList.model()
            # Make the item Black in modelList
            for i in range(mod.rowCount()):
                for j in range(mod.item(i).rowCount()):
                    if (
                        previous_current_batch_num != "NS"
                        and previous_current_piece_num != "NS"
                    ):
                        if int(previous_current_batch_num) == int(
                            mod.item(i).text()
                        ) and int(previous_current_piece_num) == int(
                            mod.item(i).child(j).text()
                        ):
                            # Make the old selected black
                            mod.item(i).child(j).setForeground(QColor("black"))
            # Make the item Black in model sorted list
            sortedMod = view.sortedModelList.model()
            for i in range(sortedMod.rowCount()):

                if (
                    previous_current_batch_num != "NS"
                    and previous_current_piece_num != "NS"
                ):

                    if (
                        sortedMod.item(i).text()
                        == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                    ):

                        (sortedMod.item(i)).setForeground(QColor("black"))
            # Also we need to unred the previous selected item in the sorted model list

            # Remove the dict entry from
            dict_key = f"{easting},{northing },{context},{int(num)}"
            view._3d_model_dict[dict_key] = (None, None)
            view.current_batch.setText(f"NS")
            view.current_piece.setText(f"NS")




    def add_match_confirm(self, e): 
        mainModel, view, controller = self.get_model_view_controller()

        if e.text() == "OK":
            easting, northing, context =  (controller.get_easting_northing_context())
            find_num = view.selected_find.text()
            batch_num = view.new_batch.text()
            piece_num = view.new_piece.text()
            previous_current_batch_num = view.current_batch.text()
            previous_current_piece_num = view.current_piece.text()

            if easting and northing and context and find_num and batch_num and piece_num:
                update_match_info(easting, northing,context, int(find_num),int(batch_num),int(piece_num))
                #Here to avoid loading time, we manually update some data. We can
                #reload the contexts but it would be way too slow

                if hasattr(view,  "selected_find_widget"):
                    view.selected_find_widget.setForeground(QColor("red"))
                view.current_batch.setText(batch_num)
                view.current_piece.setText(piece_num)
                #Here's let's try to get color red
 
                mod = view.modelList.model()
                #Make the item red in modelList
                for i in range(mod.rowCount()):

                    for j in range(mod.item(i).rowCount()):
                        if int(batch_num) == int(mod.item(i).text()) and int(piece_num) == int(mod.item(i).child(j).text()):
                            #Make the newly selected red
                            mod.item(i).child(j).setForeground(QColor("red"))
                        if previous_current_batch_num != "NS" and previous_current_piece_num != "NS":
                            if int(previous_current_batch_num) == int(mod.item(i).text()) and int(previous_current_piece_num) == int(mod.item(i).child(j).text()):
                                #Make the old selected black
                                mod.item(i).child(j).setForeground(QColor("black"))


                
                
                #Make the item red in sortedModelList
                sortedMod = view.sortedModelList.model()
                for i in range(sortedMod.rowCount()):
            
                    if sortedMod.item(i).text() == f"Batch {int(batch_num):03}, model: {int(piece_num)}":
                        (sortedMod.item(i)).setForeground(QColor("red"))       
                    if previous_current_batch_num != "NS" and previous_current_piece_num != "NS":        
                        if sortedMod.item(i).text() == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}":                      
                            (sortedMod.item(i)).setForeground(QColor("black"))
                #Also we need to unred the previous selected item in the sorted model list
                
                dict_key = f"{easting},{northing },{context},{int(find_num)}" 
                view._3d_model_dict[dict_key] = (int(batch_num), int(piece_num))
        
                
            else:
                QMessageBox(view,text="Please select both a find and a model").exec()
    def add_match(self):
            mainModel, view, controller = self.get_model_view_controller()
 
            find_num = view.selected_find.text()
            batch_num = view.new_batch.text()
            piece_num = view.new_piece.text()
            msg = QMessageBox()
            msg.setText(f"Find ({find_num}) will be updated to 3d Batch ({batch_num}) 3d Piece ({piece_num}). Proceed?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(controller.add_match_confirm)
            msg.exec()