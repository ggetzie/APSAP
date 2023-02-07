#In MVVN, Model View ViewModel architecture, Model represents the data in the application.

from config.path_variables import FINDS_SUBDIR, BATCH_3D_SUBDIR, FINDS_PHOTO_DIR, MODELS_FILES_DIR, MODELS_FILES_RE, HEMISPHERES


#here

 
 
class MainModel:
    def __init__(self, file_root):
        self.file_root = file_root

    
    def get_hemispheres(self):
        hemispheres = [
            d.name
            for d in self.file_root.iterdir()
            if d.name in HEMISPHERES and d.is_dir()
        ]
 
        return hemispheres

    def get_zones(self, path):
        res = [d.name for d in path.iterdir() if d.is_dir() and d.name.isdigit()]
        return res
