import time
from PyQt5.QtGui import (
    QStandardItemModel,
)
from PyQt5.QtCore import Qt

from config.path_variables import (
    FINDS_SUBDIR,
    BATCH_3D_SUBDIR,
    FINDS_PHOTO_DIR,
    MODELS_FILES_DIR,
    MODELS_FILES_RE,
    HEMISPHERES,
)
from model.database.database_tools import get_pottery_sherd_info, update_match_info
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QListWidgetItem,
)
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
from glob import glob as glob
from helper.misc import simple_get_json, simple_save_json
import pathlib


class TempMixin:  # bridging the view(gui) and the model(data)
    def __init__(self, view, model):
        # Notice this object is the controller, that which connects the view(GUI) and the model(data)
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
        # self.contextDisplay.setText(self.get_context_string())
        if hasattr(view, "current_pcd"):
            view.vis.remove_geometry(view.current_pcd)
            view.current_pcd = None

        model = QStandardItemModel(view)
        view.sortedModelList.setModel(model)
        funcs_to_run = [
            ["Loading finds. It might take a while", controller.populate_finds],
            ["Loading models. It might take a while", controller.populate_models],
        ]

        now = time.time()
        view.load_and_run(funcs_to_run)
        print(f"Timed passed: {time.time() - now} seconds")

    def get_context_dir(self):
        model, view, controller = self.get_model_view_controller()

        res = (
            model.file_root
            / view.hemisphere_cb.currentText()
            / view.zone_cb.currentText()
            / view.easting_cb.currentText()
            / view.northing_cb.currentText()
            / view.context_cb.currentText()
        )
        if not res.exists():
            view.statusLabel.setText(f"{res} does not exist!")
            return pathlib.Path()
        return res

    def get_easting_northing_context(self):
        model, view, controller = self.get_model_view_controller()

        context_dir = controller.get_context_dir()
        path_parts = pathlib.Path(context_dir).parts[-3:]
        easting = int(path_parts[0])
        northing = int(path_parts[1])
        context = int(path_parts[2])
        return (easting, northing, context)

    def populate_finds(self):
        # if self.splash:
        #    self.splash.showMessage("Loading finds")
        model, view, controller = self.get_model_view_controller()

        view.findsList.clear()
        context_dir = controller.get_context_dir()

        finds_dir = context_dir / FINDS_SUBDIR
        finds = [d.name for d in finds_dir.iterdir() if d.name.isdigit()]
        # Getting easting, northing and context for getting doing the query
        easting_northing_context = controller.get_easting_northing_context()
        finds.sort(key=lambda f: int(f))

        # Get a dictionary to get all
        view._3d_model_dict = dict()
        for find in finds:

            first_jpg_path = (
                controller.get_context_dir()
                / FINDS_SUBDIR
                / find
                / FINDS_PHOTO_DIR
                / "1.jpg"
            )
            second_jpg_path = (
                controller.get_context_dir()
                / FINDS_SUBDIR
                / find
                / FINDS_PHOTO_DIR
                / "2.jpg"
            )

            if (
                pathlib.Path(first_jpg_path).is_file()
                and pathlib.Path(second_jpg_path).is_file
            ):

                item = QListWidgetItem(find)
                _3d_locations = get_pottery_sherd_info(
                    easting_northing_context[0],
                    easting_northing_context[1],
                    easting_northing_context[2],
                    int(find),
                )

                if _3d_locations[0] != None and _3d_locations[1] != None:
                    item.setForeground(QColor("red"))
                view.findsList.addItem(item)
                view._3d_model_dict[
                    f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find)}"
                ] = _3d_locations

    def populate_models(self):
        import re

        # Populate all models and at the same time get the information of those models for comparison.
        mainModel, view, controller = self.get_model_view_controller()

        path = str((controller.get_context_dir() / MODELS_FILES_DIR))
        all_model_paths = glob(path)

        if not all_model_paths:
            view.statusLabel.setText(f"No models were found")
        # Setting up the model
        model = QStandardItemModel(view)
        model.setHorizontalHeaderLabels(["Models"])
        # Getting a dict for all the batches
        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(MODELS_FILES_RE, path.replace("\\", "/"))
            # This error happens when the relative path is different
            batch_num = m.group(1)
            piece_num = m.group(2)
            if batch_num not in batches_dict:
                batches_dict[batch_num] = [[int(piece_num), path]]
            else:
                batches_dict[batch_num].append([int(piece_num), path])
        # Sort the items
        for key in batches_dict:
            batches_dict[key] = sorted(batches_dict[key])

        all_matched_3d_models = set()

        for key in view._3d_model_dict:
            if not (
                view._3d_model_dict[key][0] == None
                and view._3d_model_dict[key][1] == None
            ):
                all_matched_3d_models.add(view._3d_model_dict[key])

        # Add all items onto the QTree

        # We get all the information of all the 3d models, that we can use to rank them by similarity
        actual_index = 0
        all_3d_areas = []
        all_3d_brightness_summaries = []
        all_3d_colors_summaries = []
        all_3d_width_length_summaries = []
        all_3d_area_circle_ratios = []
        import time

        now = time.time()
        for batch in batches_dict:
            items = batches_dict[batch]
            batch = QStandardItem(f"{batch}")

            for item in items:
                index = item[0]

                path = item[1]

                if path in mainModel.calculuated_paths:
                    batch_num = mainModel.calculuated_paths[path]["batch_num"]
                    piece_num = mainModel.calculuated_paths[path]["piece_num"]
                    brightness_summary = mainModel.calculuated_paths[path][
                        "brightness_summary"
                    ]
                    colors_summary = mainModel.calculuated_paths[path]["colors_summary"]
                    width_length_summary = mainModel.calculuated_paths[path][
                        "width_length_summary"
                    ]
                    area = mainModel.calculuated_paths[path]["area"]
                    index = mainModel.calculuated_paths[path]["index"]
                    context = mainModel.calculuated_paths[path]["context"]
                    cirlcle_area_ratio = mainModel.calculuated_paths[path][
                        "cirlcle_area_ratio"
                    ]

                else:

                    m = re.search(MODELS_FILES_RE, path.replace("\\", "/"))
                    # This error happens when the relative path is different
                    batch_num = m.group(1)
                    piece_num = m.group(2)

                    # Calculate the area of the current piece

                    brightness_summary = view.comparator.get_brightness_summary_from_3d(
                        path
                    )
                    brightness_summary = list(brightness_summary)

                    # Calculate the color summary of the current piece
                    colors_summary = view.comparator.get_color_summary_from_3d(path)
                    colors_summary = list(colors_summary)
                    (
                        area,
                        width_length_summary,
                    ) = view.comparator.get_3d_object_area_and_width_length(path)

                    cirlcle_area_ratio = view.comparator.get_3d_area_circle_ratio(path)
                    width_length_summary = list(width_length_summary)
                    json_data = mainModel.json_data
                    temp = {}
                    temp["path"] = path
                    temp["index"] = index
                    temp["batch_num"] = batch_num
                    temp["piece_num"] = piece_num

                    temp["cirlcle_area_ratio"] = cirlcle_area_ratio
                    temp["brightness_summary"] = brightness_summary
                    temp["colors_summary"] = colors_summary
                    temp["area"] = area
                    temp["width_length_summary"] = width_length_summary
                    temp["context"] = view.context_cb.currentText()
                    temp["zone"] = view.zone_cb.currentText()
                    temp["hemisphere"] = view.hemisphere_cb.currentText()
                    temp["utm_easting"] = view.easting_cb.currentText()
                    temp["utm_northing"] = view.northing_cb.currentText()

                    json_data["past_records"].append(temp)
                all_3d_colors_summaries.append(colors_summary)
                print(f"index: {actual_index}: 3dArea: {area}")

                # Here we better save the information
                all_3d_area_circle_ratios.append(
                    [cirlcle_area_ratio, batch_num, piece_num]
                )
                all_3d_areas.append([area, batch_num, piece_num])
                all_3d_brightness_summaries.append(
                    [brightness_summary, batch_num, piece_num]
                )
                all_3d_width_length_summaries.append(
                    [width_length_summary, batch_num, piece_num]
                )
                ply = QStandardItem(f"{index}")
                ply.setData(f"{path}", Qt.UserRole)
                if (int(batch_num), int(piece_num)) in all_matched_3d_models:
                    ply.setForeground(QColor("red"))
                batch.appendRow(ply)
                actual_index += 1
            model.appendRow(batch)
        simple_save_json(mainModel.json_data, "./parameters/data/data.json")

        print(f"{time.time() - now} seconds")
        view.all_3d_areas = all_3d_areas
        view.all_3d_width_length_summaries = all_3d_width_length_summaries
        view.all_3d_brightness_summaries = all_3d_brightness_summaries
        view.all_3d_area_circle_ratios = all_3d_area_circle_ratios
        view.all_3d_colors_summaries = all_3d_colors_summaries
        view.modelList.setModel(model)
        view.modelList.selectionModel().currentChanged.connect(view.change_3d_model)
