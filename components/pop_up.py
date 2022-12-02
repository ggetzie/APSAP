#This class contains classes and functiosn related to functionalities related to pop_up
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QListWidgetItem, QFileDialog, QMessageBox, QSplashScreen
import pathlib
import json
from glob import glob as glob
from database_tools import update_match_info
from PyQt5.QtGui import QColor, QIcon, QPixmap, QImage, QWindow, QStandardItem, QStandardItemModel, QMovie, QPainter

class LoadingSplash(QSplashScreen):
    
    def mousePressEvent(self, event):
        # disable default "click-to-dismiss" behaviour
        pass
    
class PopUp():

    def load_and_run(self, funcs_to_run):
        #Load the splash
        splash = LoadingSplash()
        splash.show()
        #Run all functions and the message during loading time
        for message_func in funcs_to_run:
            message = message_func[0]
            func = message_func[1]
            splash.showMessage(message)
            func()
        #Close the window    
        window = QMainWindow()
        window.show()
        splash.finish(window)
      
    
    def ask_for_prompt(self):
        Title = "Please enter the file path!"
        while True:
            
            QMessageBox(self,text="Please select a path to the files").exec()
            dlg = QFileDialog(self)
            dlg.setFileMode(QFileDialog.Directory)
            dlg.resize(600,100)                    
            dlg.setWindowTitle(Title)
            dlg.exec()
            text = dlg.selectedFiles()[0]
            
            if (pathlib.Path(text).is_dir()):
                has_N_S = (any([pathlib.Path(path).stem == "N" or pathlib.Path(path).stem == "S" for path in glob(f"{text}/*")]))
                if has_N_S:
                    #This is when the path is actually nice enough that we can save it
                    true_path = text
                    if not pathlib.Path("./settings.json").is_file():
                        #In this case, we can make a settings from scratch
                        file_dict = {"FILE_ROOT": f"{true_path}"}

                    else:
                        f = open('settings.json')
                        #Whether if the key is not there  or the path doesn't exist, we are sure we can save it in the dict now
                        file_dict = json.load(f)                        
                        file_dict["FILE_ROOT"] = true_path
                        f.close()
                    with open('settings.json', 'w') as fp:
                            json.dump(file_dict, fp)
                            fp.close()
                    break    
                else:
                    Title = "Valid paths must contain a directory named N or S!"
            else:
                Title = "Path doesn't exist"
                
    def check_has_path_in_setting(self):
        setting_found = pathlib.Path("./settings.json").is_file()  
        if not setting_found:
            return False
        else:
            setting_dict = json.load(open("settings.json")) if setting_found else {}  
            key_exist = "FILE_ROOT" in setting_dict
            if key_exist:
                path_exist =  pathlib.Path(setting_dict["FILE_ROOT"]).is_dir()
                if path_exist: #Only case when we don't have to ask for a path
                    return True
                else:
                    return False
            else:
                return False

    def update_button_click(self, e):
        if e.text() == "OK":
            easting, northing, context =  (self.get_easting_northing_context())
            find_num = self.selected_find.text()
            batch_num = self.new_batch.text()
            piece_num = self.new_piece.text()
            if easting and northing and context and find_num and batch_num and piece_num:
                update_match_info(easting, northing,context, int(find_num),int(batch_num),int(piece_num))
                #Here to avoid loading time, we manually update some data. We can
                #reload the contexts but it would be way too slow
                batch_num = self.new_batch.text()
                piece_num = self.new_piece.text()
                if hasattr(self,  "selected_find_widget"):
                    self.selected_find_widget.setForeground(QColor("red"))
                self.current_batch.setText(batch_num)
                self.current_piece.setText(piece_num)
                #Here's let's try to get color red
 
                mod = self.modelList.model()
                #Make the item red in modelList
                for i in range(mod.rowCount()):

                    for j in range(mod.item(i).rowCount()):
                        if int(batch_num) == int(mod.item(i).text()) and int(piece_num) == int(mod.item(i).child(j).text()):
                            mod.item(i).child(j).setForeground(QColor("red"))
                #Make the item red in sortedModelList
                sortedMod = self.sortedModelList.model()
                for i in range(sortedMod.rowCount()):
                    #f"{int(_3d_locations[0]):03}", 1).replace("*", f"{int(_3d_locations[1])}
                    if sortedMod.item(i).text() == f"Batch {int(batch_num):03}, model: {int(piece_num)}":
                        (sortedMod.item(i)).setForeground(QColor("red"))
            else:
                QMessageBox(self,text="Please select both a find and a model").exec()
    def update_model_db(self):
 
            find_num = self.selected_find.text()
            batch_num = self.new_batch.text()
            piece_num = self.new_piece.text()
            msg = QMessageBox()
            msg.setText(f"Find ({find_num}) will be updated to 3d Batch ({batch_num}) 3d Piece ({piece_num}). Proceed?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.buttonClicked.connect(self.update_button_click)
            msg.exec()