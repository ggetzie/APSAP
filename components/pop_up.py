#This class is inherited for the pop-up loading and prompt functionality
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QListWidgetItem, QFileDialog, QMessageBox, QSplashScreen
import pathlib
import json
from glob import glob as glob


class LoadingSplash(QSplashScreen):
    
    def mousePressEvent(self, event):
        # disable default "click-to-dismiss" behaviour
        pass
    
class PopUp():

    def load_and_run(self, funcs_to_run):
        #Load the splash
        splash = LoadingSplash()
        splash.show()
        #Run all functions
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
    