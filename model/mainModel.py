#In MVVN, Model View ViewModel architecture, Model represents the data in the application.

from config.path_variables import FINDS_SUBDIR, BATCH_3D_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR, MODELS_FILES_RE, HEMISPHERES
from helper.misc import simple_get_json
import pathlib, json
#here

 
 
class MainModel:
    def __init__(self):

        if not self.check_has_path_in_setting():
            self.ask_for_prompt()
        setting = json.load(open("./configs/settings.json"))

        self.file_root = pathlib.Path(setting["FILE_ROOT"] )
        self.json_data = simple_get_json("./configs/data.json")
    
        self.parameters = simple_get_json("./configs/parameters.json")
        calculuated_paths = dict()
        for obj in self.json_data["past_records"]:
            calculuated_paths[obj["path"]] = obj
        self.calculuated_paths = calculuated_paths

 

    def get_hemispheres(self):
        hemispheres = [
            d.name
            for d in self.file_root.iterdir()
            if d.name in HEMISPHERES and d.is_dir()
        ]
 
        return hemispheres


    def get_options(self, path):
        res = [d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()]
        return res

    def check_has_path_in_setting(self):
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

    
    def ask_for_prompt(self): #Although this technically involves a lot of code of GUI(as a pop up), it is in here instead of View because this function ensures that settings are well imported before we run the application
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
                    Title = "Valid paths must contain a directory named N or S!"
            else:
                Title = "Path doesn't exist"
                
 