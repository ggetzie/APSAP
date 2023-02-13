#In MVVN, Model View ViewModel architecture, Model represents the data in the application.
from PyQt5.QtWidgets import  QMessageBox, QFileDialog
import pathlib, json
from glob import glob as glob

#here
class InitialLoadMixin:
 
    def prepare_data(self, main_view):
        self.request_path(main_view)
        setting = self.simple_get_json("./configs/settings.json")
        self.file_root = pathlib.Path(setting["FILE_ROOT"] )
        self.json_data = self.simple_get_json("./configs/cache.json")
        self.parameters = self.simple_get_json("./configs/parameters.json")
        self.calculuated_paths = self.get_path_object_dict(self.json_data["past_records"])
        self.path_variables = self.simple_get_json("./configs/pathVariables.json")

    def get_path_object_dict(self, past_records):
        calculuated_paths = dict()
        
        for obj in past_records:
            calculuated_paths[obj["path"]] = obj
        
        return calculuated_paths


    def vali_path_exists(self):
        setting_found = pathlib.Path("./configs/settings.json").is_file()  
        if not setting_found:
            return False
        else:
            setting_dict = json.load(open("./configs/settings.json")) if setting_found else {}  
            key_exist = "FILE_ROOT" in setting_dict
            if key_exist:
                path_exist =  pathlib.Path(setting_dict["FILE_ROOT"]).is_dir()
                if path_exist: #Only case when we don't have to ask for a path
                    return True
                else:
                    return False
            else:
                return False


    def request_path(self, main_view): #Although this technically involves a lot of code of GUI(as a pop up), it is in here instead of View because this function ensures that settings are well imported before we run the application
        if not self.vali_path_exists():
            title = "Please enter the file path!"
            while True:
                
                QMessageBox(main_view,text="Please select a path to the files").exec()
                dlg = QFileDialog(main_view)
                dlg.setFileMode(QFileDialog.Directory)
                dlg.resize(600,100)                    
                dlg.setWindowTitle(title)
                dlg.exec()
                text = dlg.selectedFiles()[0]
                
                if (pathlib.Path(text).is_dir()):
                    has_N_S = (any([pathlib.Path(path).stem == "N" or pathlib.Path(path).stem == "S" for path in glob(f"{text}/*")]))
                    if has_N_S:
                        #This is when the path is actually nice enough that we can save it
                        true_path = text
                        if not pathlib.Path("./configs/settings.json").is_file():
                            #In this case, we can make a settings from scratch
                            file_dict = {"FILE_ROOT": f"{true_path}"}

                        else:
                            f = open('./configs/settings.json')
                            #Whether if the key is not there  or the path doesn't exist, we are sure we can save it in the dict now
                            file_dict = json.load(f)                        
                            file_dict["FILE_ROOT"] = true_path
                            f.close()
                        with open('./configs/settings.json', 'w') as fp:
                                json.dump(file_dict, fp)
                                fp.close()
                        break    
                    else:
                        title = "Valid paths must contain a directory named N or S!"
                else:
                    title = "Path doesn't exist"
                    
    