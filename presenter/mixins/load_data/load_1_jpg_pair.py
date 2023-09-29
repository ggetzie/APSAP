from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PIL.ImageQt import ImageQt
import open3d as o3d
import time


class Load1jpgPairMixin:  # bridging the view(gui) and the model(data)
    def load_find_images(self, selected_item):
        """This function would try to load the two images into the GUI and after finishing its operations,
        load the sorted 3d models.

        Args:
            selected_item (_type_): _description_
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        # Set the currenly selected item
     

        # We test two things to see if we discard the subsequent operations of this function
        # 1. We check of the current selected item has text
        # 2. We check if the two supposedly existent pictures exist and are openable by the user
        # according to her access rights.
        try:
            find_num = main_view.finds_list.currentItem().text()

        except AttributeError:
            main_view.findFrontPhoto_l.clear()
            main_view.findBackPhoto_l.clear()
            return

        main_view.selected_find_widget = selected_item

        # Set photo directory of the current selected find
        photos_dir = (
            main_presenter.get_context_dir()
            / main_model.path_variables["FINDS_SUBDIR"]
            / find_num
            / main_model.path_variables["FINDS_PHOTO_DIR"]
        )

        main_view.path_2d_picture = photos_dir
        
        try:
            front_photo = ImageQt(main_model.open_image(str(photos_dir / "1.jpg")))
            back_photo = ImageQt(main_model.open_image(str(photos_dir / "2.jpg")))
        except:
            from PyQt5.QtWidgets import QMessageBox

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText(f"The jpegs in {photos_dir} are not openable")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        # Set up the front image to be displayed
        main_view.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(
                main_view.findFrontPhoto_l.width()
            )
        )

        # Set up the path so that the image can be opened at a small window
        main_view.current_image_front = str(photos_dir / "1.jpg")

        # Set up the back image to be displayed
        main_view.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(
                main_view.findBackPhoto_l.width()
            )
        )

        # Set up the path so that the image can be opened at a small window
        main_view.current_image_back = str(photos_dir / "2.jpg")

        # Set up the selected_find's text
        main_view.selected_find.setText(find_num)

        # We immediately try to load all 3d models but sorted according to their similarity with the current find
        main_presenter.load_sorted_models(selected_item)

    def load_sorted_models(self, selected_item):
        """This function load the 3d models sorted by how similiar they are with respected to the selectec
        image.

        Args:
            selected_item (object): The selected object in the list that represends a find
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        # We don't allow interactions with the GUI if we are loading the 3d models
        main_view.blockSignals(True)

        # If nothing is selectted, we simply return and do nothing
        if not (selected_item):
            main_view.blockSignals(False)
            return

        # Create a find_str so we can check if the current find has a 3d model already matched before
        easting_northing_context = main_presenter.get_easting_northing_context()
        find_str = f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(selected_item.text())}"

        if (
            find_str in main_view.dict_find_2_ply
            and main_view.dict_find_2_ply[find_str] != None
        ):
            ply_str = main_view.dict_find_2_ply[find_str]
            (batch_year, batch_num, batch_piece) = ply_str.split(",")
            main_view.current_year.setText(str(batch_year))
            main_view.current_batch.setText(str(batch_num))
            main_view.current_piece.setText(str(batch_piece))

        else:
            main_view.current_year.setText("NS")
            main_view.current_batch.setText("NS")
            main_view.current_piece.setText("NS")
            main_presenter.clean_ply_window()

        # Generate a list of 3d models sorted by similarity.
        path_2d = main_view.path_2d_picture
        models_sorted_by_similarity = (
            main_presenter.get_potential_3d_models_sorted_by_similarity(path_2d)
        )

        # Create a new model to contain these
        model = QStandardItemModel(main_view)
        model.setHorizontalHeaderLabels(["Sorted models"])

        # Go through all models, each model represented by a batch, piece and a year
        for batch_num, piece_num, year in models_sorted_by_similarity:
            # If the year is not within the filter, we ignore this 3d model
            if int(year) != int(main_view.year.value()):
                continue

            # If the batch is outside the filter, we ignore this 3d model
            if int(batch_num) < int(main_view.batch_start.value()) or int(
                batch_num
            ) > int(main_view.batch_end.value()):
                continue

            # Now the 3d model is guranteed to be a legitimate one, we add it to the an item
            ply = QStandardItem(f"{year}, Batch {batch_num}, model: {piece_num}")

            # We check if the 3d model is matched with a find, if it is we set the item to be red
            ply_str = f"{int(year)},{int(batch_num)},{int(piece_num)}"
            if ply_str in main_view.dict_ply_2_find:
                ply.setForeground(QColor("red"))

            #We save the 3d model path to the item as well
            whole_path = (
            str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
            .replace("*", str(year), 1)
            .replace("*", f"{int(batch_num):03}", 1)
            .replace("*", f"{int(piece_num)}", 1)
            )
            ply.setData(f"{whole_path}", Qt.UserRole)

            #Finally we add the item to the model
            model.appendRow(ply)

        
        main_presenter.clean_ply_window()

        #Reset the list that contains the sorted 3d models
        main_view.sorted_model_list.setModel(model)
        main_view.sorted_model_list.selectionModel().currentChanged.connect(
            main_presenter.change_3d_model
        )

        #Reenable interaction with the GUI
        main_view.blockSignals(False)
