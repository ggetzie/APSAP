#In MVVN, Model View ViewModel architecture, Model represents the data in the application.
from PyQt5.QtWidgets import  QMessageBox, QFileDialog
import json
from pathlib import Path
from glob import glob as glob

#here
class InitialLoadMixin:
 
    def prepare_data(self, main_view):
        self.request_path(main_view)
        setting = self.simple_get_json("./configs/settings.json")
        self.file_root = Path(setting["FILE_ROOT"] )
        self.parameters = self.simple_get_json("./configs/parameters.json")
        temp_ply= self.simple_get_json(r".\computation\saved__measurement_ply_data.json")
        temp_jpg= self.simple_get_json(r".\computation\saved__measurement_jpg_data.json")

        self.path_info_dict = self.get_path_info_dict(temp_ply, temp_jpg)
        self.path_variables = self.simple_get_json("./configs/pathVariables.json")





    def request_path(self, main_view):  
        
        if not self.vali_path_exists():
            title = "Please enter the file path!"
            while True:
                true_path = self.ask_for_path_to_files(main_view, title)
                if (Path(true_path).is_dir()):
                    has_N_S = (any([Path(path).stem == "N" or Path(path).stem == "S" for path in glob(f"{true_path}/*")]))
                    if has_N_S:
                        #This is when the path is actually nice enough that we can save it
                        if not Path("./configs/settings.json").is_file():
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

    def ask_for_path_to_files(self,main_view, title ):
    
        QMessageBox(main_view, text="Please select a path to the files").exec()
        dlg = QFileDialog(main_view)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.resize(600,100)                    
        dlg.setWindowTitle(title)
        dlg.exec()
        return dlg.selectedFiles()[0]

    def vali_path_exists(self):
        setting_found = Path("./configs/settings.json").is_file()  
        if setting_found:
            setting_dict = json.load(open("./configs/settings.json")) 
            if "FILE_ROOT" in setting_dict:
                if Path(setting_dict["FILE_ROOT"]).is_dir(): 
                    return True
                
        return False

    def get_path_info_dict(self, past_ply_records, past_jpg_records):
        #Calculuaterd paths have "path" as the key to "the path's object;s calculuated area, brigthness extra "'s value
        path_info_dict = dict()
        
        for obj in past_ply_records:
            path_info_dict[obj["path"]] = obj
        for obj in past_jpg_records:
            if "img_1_path" in obj:

                path_info_dict[obj["img_1_path"]] = {
                    "area_img_1": obj["area_img_1"],
                    "light_ima_1": obj["light_ima_1"],
                    "img_1_width_length": obj["img_1_width_length"],
                    "img_1_path": obj["img_1_path"]
                }
            elif "img_2_path" in obj:
               
                path_info_dict[obj["img_2_path"]] = {
                    "area_img_2": obj["area_img_2"],
                    "light_ima_2": obj["light_ima_2"],
                    "img_2_width_length": obj["img_2_width_length"],
                    "img_2_path": obj["img_2_path"]
                } 
        return path_info_dict