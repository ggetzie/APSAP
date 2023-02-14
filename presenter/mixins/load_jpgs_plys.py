import time

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QListWidgetItem,
)
from PyQt5.QtGui import (
    QColor,
    QStandardItem,
    QStandardItemModel,
)
from glob import glob as glob
import pathlib


class LoadJpgsPlysMixin:  # bridging the view(gui) and the model(data)
    def get_context_dir(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        res = (
            main_model.file_root
            / main_view.hemisphere_cb.currentText()
            / main_view.zone_cb.currentText()
            / main_view.easting_cb.currentText()
            / main_view.northing_cb.currentText()
            / main_view.context_cb.currentText()
        )
        if not res.exists():
            main_view.statusLabel.setText(f"{res} does not exist!")
            return pathlib.Path()
        return res

    def get_easting_northing_context(self):
        main_model, view, main_presenter = self.get_model_view_presenter()

        context_dir = main_presenter.get_context_dir()
        path_parts = pathlib.Path(context_dir).parts[-3:]
        easting = int(path_parts[0])
        northing = int(path_parts[1])
        context = int(path_parts[2])
        return (easting, northing, context)

    def populate_finds(self):

        main_model, main_view, main_presenter = self.get_model_view_presenter()

        main_view.finds_list.clear()
        context_dir = main_presenter.get_context_dir()

        finds_dir = context_dir / main_model.path_variables["FINDS_SUBDIR"]
        finds = [d.name for d in finds_dir.iterdir() if d.name.isdigit()]
        # Getting easting, northing and context for getting doing the query
        easting_northing_context = main_presenter.get_easting_northing_context()
        finds.sort(key=lambda f: int(f))

        # Get a dictionary to get all
        main_view._3d_model_dict = dict()
        for find in finds:

            first_jpg_path = (
                main_presenter.get_context_dir()
                / main_model.path_variables["FINDS_SUBDIR"]
                / find
                / main_model.path_variables["FINDS_PHOTO_DIR"]
                / "1.jpg"
            )
            second_jpg_path = (
                main_presenter.get_context_dir()
                / main_model.path_variables["FINDS_SUBDIR"]
                / find
                / main_model.path_variables["FINDS_PHOTO_DIR"]
                / "2.jpg"
            )

            if (
                pathlib.Path(first_jpg_path).is_file()
                and pathlib.Path(second_jpg_path).is_file
            ):

                item = QListWidgetItem(find)
                _3d_locations = main_model.get_pottery_sherd_info(
                    easting_northing_context[0],
                    easting_northing_context[1],
                    easting_northing_context[2],
                    int(find),
                )

                if _3d_locations[0] != None and _3d_locations[1] != None:
                    item.setForeground(QColor("red"))
                main_view.finds_list.addItem(item)
                main_view._3d_model_dict[
                    f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find)}"
                ] = _3d_locations

    def populate_models(self):
        import re

        # Populate all models and at the same time get the information of those models for comparison.
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        path = str(
            (
                main_presenter.get_context_dir()
                / main_model.path_variables["MODELS_FILES_DIR"]
            )
        )
        all_model_paths = glob(path)

        if not all_model_paths:
            main_view.statusLabel.setText(f"No models were found")
        # Setting up the model
        model = QStandardItemModel(main_view)
        model.setHorizontalHeaderLabels(["Models"])
        # Getting a dict for all the batches
        batches_dict = dict()
        for path in all_model_paths:
            m = re.search(
                main_model.path_variables["MODELS_FILES_RE"], path.replace("\\", "/")
            )
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

        for key in main_view._3d_model_dict:
            if not (
                main_view._3d_model_dict[key][0] == None
                and main_view._3d_model_dict[key][1] == None
            ):
                all_matched_3d_models.add(main_view._3d_model_dict[key])

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

                if path in main_model.calculuated_paths:
                    batch_num = main_model.calculuated_paths[path]["batch_num"]
                    piece_num = main_model.calculuated_paths[path]["piece_num"]
                    brightness_summary = main_model.calculuated_paths[path][
                        "brightness_summary"
                    ]
                    colors_summary = main_model.calculuated_paths[path][
                        "colors_summary"
                    ]
                    width_length_summary = main_model.calculuated_paths[path][
                        "width_length_summary"
                    ]
                    area = main_model.calculuated_paths[path]["area"]
                    index = main_model.calculuated_paths[path]["index"]
                    context = main_model.calculuated_paths[path]["context"]
                    cirlcle_area_ratio = main_model.calculuated_paths[path][
                        "cirlcle_area_ratio"
                    ]

                else:

                    m = re.search(
                        main_model.path_variables["MODELS_FILES_RE"],
                        path.replace("\\", "/"),
                    )
                    # This error happens when the relative path is different
                    batch_num = m.group(1)
                    piece_num = m.group(2)

                    # Calculate the area of the current piece

                    brightness_summary = main_presenter.get_brightness_summary_from_3d(
                        path
                    )
                    brightness_summary = list(brightness_summary)

                    # Calculate the color summary of the current piece
                    colors_summary = main_presenter.get_color_summary_from_3d(path)
                    colors_summary = list(colors_summary)
                    (
                        area,
                        width_length_summary,
                    ) = main_presenter.get_3d_object_area_and_width_length(path)

                    cirlcle_area_ratio = main_presenter.get_3d_area_circle_ratio(path)
                    width_length_summary = list(width_length_summary)
                    json_data = main_model.json_data
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
                    temp["context"] = main_view.context_cb.currentText()
                    temp["zone"] = main_view.zone_cb.currentText()
                    temp["hemisphere"] = main_view.hemisphere_cb.currentText()
                    temp["utm_easting"] = main_view.easting_cb.currentText()
                    temp["utm_northing"] = main_view.northing_cb.currentText()

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
        main_model.simple_save_json(main_model.json_data, "./configs/cache.json")

        print(f"{time.time() - now} seconds")
        main_view.all_3d_areas = all_3d_areas
        main_view.all_3d_width_length_summaries = all_3d_width_length_summaries
        main_view.all_3d_brightness_summaries = all_3d_brightness_summaries
        main_view.all_3d_area_circle_ratios = all_3d_area_circle_ratios
        main_view.all_3d_colors_summaries = all_3d_colors_summaries
        main_view.modelList.setModel(model)
        main_view.modelList.selectionModel().currentChanged.connect(
            main_presenter.change_3d_model
        )
