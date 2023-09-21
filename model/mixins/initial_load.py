from PyQt5.QtWidgets import QMessageBox, QFileDialog
import json
from pathlib import Path
from glob import glob as glob
from diskcache import Cache


class InitialLoadMixin:
    def prepare_data(self, main_view):
        """This function prepares all the data that needs to be preliminarily loaded before the application begins.

        Args:
            main_view (QT Window widget): This is the widget that contains GUI related functions and classes
        """

        # Data 1: Loading the root of the 3d model and 2d jpegs files.
        self.ensure_settings_exists(main_view)
        setting = self.simple_get_json("./configs/settings.json")
        self.file_root = Path(setting["FILE_ROOT"])

        # Data 2: Loading the Cache object of the measured data of the 3d models and 2d jpegs
        self.cache_3d = Cache("./cache/cache_3d_new")
        self.cache_2d = Cache("./cache/cache_2d_new")

        # Data 3: Loading the parameters(For similarities calculuations) and path_variables(for locating specific paths)
        self.parameters = self.simple_get_json("./configs/parameters.json")
        self.path_variables = self.simple_get_json("./configs/pathVariables.json")

        # Data 4: An dummy image here is needed for what we need
        self.reference_place_holder_img = "computation/reference_placeholder.jpg"

    def ensure_settings_exists(self, main_view):
        """This function will keep asking the user to select a folder to the root of the files if there isn't one already

        Args:
            main_view (QT Window widget): This is the widget that contains GUI related functions and classes
        """

        if self.setting_file_exists():
            return

        message = "Please enter the file path!"
        while True:
            # Test 1: The file path the user just chose is a valid directory?
            chosen_path = self.ask_for_path_to_files(main_view, message)
            if not (Path(chosen_path).is_dir()):
                message = "Path doesn't exist"
                continue

            # Test 2: The file path's directory contains an N or an S.
            has_N_S = any(
                [
                    Path(path).stem == "N" or Path(path).stem == "S"
                    for path in glob(f"{chosen_path}/*")
                ]
            )
            if not has_N_S:
                message = "Valid paths must contain a directory named N or S!"
                continue

            # We save the json file
            file_dict = {"FILE_ROOT": f"{chosen_path}"}
            with open("./configs/settings.json", "w") as fp:
                json.dump(file_dict, fp)
                fp.close()
            # If a saving operation is successful we immediately return
            return

    def ask_for_path_to_files(self, main_view, message):
        """This function asks the user to locate the root folder for the 3d models and 2d images

        Args:
            main_view (QT Window widget): This is the widget that contains GUI related functions and classes
            message (str): The message that gets displayed to ask the user to input the correct folder.

        Returns:
            str: The directory that user just chose
        """
        QMessageBox(main_view, text="Please select a path to the files").exec()
        dlg = QFileDialog(main_view)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.resize(600, 100)
        dlg.setWindowTitle(message)
        dlg.exec()
        return dlg.selectedFiles()[0]

    def setting_file_exists(self):
        """This function checks if the settings.json file exists or not

        Returns:
            boolean: True if all the tests are passed. False Otherwise
        """
        # Test 1: Check if the file exists
        setting_json_found = Path("./configs/settings.json").is_file()
        if not setting_json_found:
            return False

        # Test 2: Check if the json file has valid json
        try:
            setting_dict = json.load(open("./configs/settings.json"))
        except:
            return False

        # Test 3: Check if the key FILE_ROOT is in the json object
        if "FILE_ROOT" not in setting_dict:
            return False

        # Test 4: Check if the FILE_ROOT desiginated is a valid directory.
        if not Path(setting_dict["FILE_ROOT"]).is_dir():
            return False

        # All Tests are passed, so we have a valid setting file
        return True
