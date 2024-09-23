import logging
from pathlib import Path

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox


def batch_piece_year_valid(batch_num, piece_num, year):
    """This function checks if the piece number and year are valid

    Args:
        num_piece (str): The piece number
        year (str): The year

    Returns:
        bool: True if the piece number and year are valid, False otherwise
    """
    return all(x is not None and x != "NS" for x in [batch_num, piece_num, year])


class AddAndRemoveMatchMixin:
    """This class contains the functions that handle modifying an entry at the database.
    Notice that we need confirmation before the database operations are being done to make
    it more secure
    """

    def add_match(self):
        """This function creates a pop up box that asks if the user wants to confirm
        adding the match"""
        _, main_view, main_presenter = self.get_model_view_presenter()

        # Create the message to be shown
        find_num = main_view.selected_find.text()
        batch_num = main_view.new_batch.text()
        piece_num = main_view.new_piece.text()
        year_num = main_view.new_year.text()
        msg = QMessageBox(
            main_view,
            text=(
                f"Update Find ({find_num}) to batch ({batch_num}) piece "
                f"({piece_num}) year ({year_num}). Proceed?"
            ),
        )

        # Set the buttons and callback to the buttons
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(main_presenter.add_match_confirm)

        # Show the pop up with buttons ok and cancel
        msg.exec()

    def add_match_confirm(self, e):
        """This function tries to do two things when the ok button is clicked for add_match.
        First, it tries to update the database to reflect the matched result.
        Second, it tries to fix the added ceramic sherds and put them to the find folder.
        These sherds include the original-sized one and the

        Args:
            (button): The button that get clicked on.
        """
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        # In case that the button clicked is "OK"(e.g. Cancel), we don't do anything
        if not e.text() == "OK":
            return

        # Get all needed to update the database
        easting, northing, context = main_presenter.get_easting_northing_context()
        find_num = main_view.selected_find.text()
        batch_num = main_view.new_batch.text()
        piece_num = main_view.new_piece.text()
        new_year: str = main_view.new_year.text()

        # If either of the of these parameters is None, we do not update the database
        if (
            any(
                x is None
                for x in [
                    easting,
                    northing,
                    context,
                    find_num,
                    batch_num,
                    piece_num,
                    new_year,
                ]
            )
            or not new_year.isnumeric()
        ):
            QMessageBox(main_view, text="Please select both a find and a model").exec()
            return

        ##Updating the database
        main_model.update_match_info(
            easting, northing, context, find_num, batch_num, piece_num, new_year
        )

        # Create the folder in which we will put the 3d models (a subfolder in the find folder)
        context_dir = main_presenter.get_context_dir()
        finds_subdir = main_model.path_variables["FINDS_SUBDIR"]
        folder = context_dir / finds_subdir / str(find_num) / "3d" / "gp"

        # Here we reconstruct the path to the 0.3 mesh 3d model
        mesh_ply_path_re = str(
            (
                main_presenter.get_context_dir()
                / main_model.path_variables["MODELS_FILES_DIR"]
            )
        )

        mesh_path = (
            mesh_ply_path_re.replace("*", str(new_year), 1)
            .replace("*", f"{int(batch_num):03}", 1)
            .replace("*", f"{int(piece_num)}", 1)
        )

        # We have reconstructed the path to the 0.3 mesh ply. Now we can get 3 more extra paths
        # So that we can put both the 0.3 mesh and original ply to the find folder
        orig_path = mesh_path.replace("_sample0_3_mesh.ply", ".ply", 1)
        original_destination = Path(folder / "a.ply")
        mesh_destination = Path(folder / "a_0_3_mesh.ply")

        # Create the folder of the destination in case it doesn't exist
        Path(str(context_dir / finds_subdir / str(find_num) / "3d" / "gp")).mkdir(
            parents=True, exist_ok=True
        )

        # We copy the files to the destination
        logging.info("Copying file from %s to %s", orig_path, original_destination)
        main_model.fix_and_copy_ply(
            str(Path(orig_path)), str(Path(original_destination))
        )
        logging.info("Copying file from %s to %s", mesh_path, mesh_destination)
        main_model.fix_and_copy_ply(str(Path(mesh_path)), str(Path(mesh_destination)))

        # We save the batch, piece and year that will get replaced later
        previous_current_batch_num = main_view.current_batch.text()
        previous_current_piece_num = main_view.current_piece.text()
        previous_current_year = main_view.current_year.text()

        # We turn the selected find_widget as red to indicate that the item is matched
        if hasattr(main_view, "selected_find_widget"):
            main_view.selected_find_widget.setForeground(QColor("red"))

        # Update on the GUI that the find has the new matched 3d model
        main_view.current_batch.setText(batch_num)
        main_view.current_piece.setText(piece_num)
        main_view.current_year.setText(new_year)

        # Here's let's try to get color red

        mod = main_view.modelList.model()
        # Make the item red in modelList

        # Go through the unsorted model that stores year, batch and piece.
        # If it is the previously selected model, we turn it black from red
        # If it is the newly selected model that we just updated we turn it red.
        for i in range(mod.rowCount()):
            for j in range(mod.item(i).rowCount()):
                for k in range(mod.item(i).child(j).rowCount()):
                    if batch_piece_year_valid(
                        previous_current_batch_num,
                        previous_current_piece_num,
                        previous_current_year,
                    ):
                        if (
                            int(previous_current_year) == int(mod.item(i).text())
                            and int(previous_current_batch_num)
                            == int(mod.item(i).child(j).text())
                            and int(previous_current_piece_num)
                            == int(mod.item(i).child(j).child(k).text())
                        ):
                            mod.item(i).child(j).child(k).setForeground(QColor("black"))
                    if (
                        int(new_year) == int(mod.item(i).text())
                        and int(batch_num) == int(mod.item(i).child(j).text())
                        and int(piece_num) == int(mod.item(i).child(j).child(k).text())
                    ):
                        mod.item(i).child(j).child(k).setForeground(QColor("red"))

        # Go through the sorted list to turn previously matched model to black and the newly
        # matched model to black
        sorted_mod = main_view.sorted_model_list.model()
        for i in range(sorted_mod.rowCount()):
            if batch_piece_year_valid(
                previous_current_batch_num,
                previous_current_piece_num,
                previous_current_year,
            ):
                to_match = (
                    f"{previous_current_year}, Batch {int(previous_current_batch_num):03}, "
                    f"model: {int(previous_current_piece_num)}"
                )
                if sorted_mod.item(i).text() == to_match:
                    (sorted_mod.item(i)).setForeground(QColor("black"))
            if (
                sorted_mod.item(i).text()
                == f"{new_year}, Batch {int(batch_num):03}, model: {int(piece_num)}"
            ):
                (sorted_mod.item(i)).setForeground(QColor("red"))

        # Here we search through all find we saved the updated matching info for
        # in the two dicts to inform later that what is matched to what
        find_str = f"{easting},{northing},{context},{int(find_num)}"
        ply_str = f"{int(new_year)},{int(batch_num)},{int(piece_num)}"
        main_view.dict_find_2_ply[find_str] = ply_str

        # We match a previous matched find only if it is inside the dict and it is a different
        # find from the find we just updated
        if (
            ply_str in main_view.dict_ply_2_find
            and main_view.dict_ply_2_find[ply_str] is not None
            and main_view.dict_ply_2_find[ply_str] != find_str
        ):
            # This means that there is a previous find matched to this 3d model
            previous_matched_find_num = main_view.dict_ply_2_find[ply_str].split(",")[
                -1
            ]
            logging.info(
                (
                    "There is a previous find_num matched to this element: %s, "
                    "we now will attempt to un-match that "
                ),
                previous_matched_find_num,
            )

            for index in range(main_view.finds_list.count()):
                if main_view.finds_list.item(index).text() == str(
                    previous_matched_find_num
                ):
                    logging.info(
                        "We have a previous find matched with this ply, the find number is : %s",
                        previous_matched_find_num,
                    )
                    # Updating to database
                    main_model.update_match_info(
                        easting,
                        northing,
                        context,
                        str(previous_matched_find_num),
                        None,
                        None,
                        None,
                    )
                    # Updating the color to black
                    main_view.finds_list.item(index).setForeground(QColor("black"))
                    # Saving the data to make the application know that the previously
                    # match find is not matched anymore
                    previously_matched_key = main_view.dict_ply_2_find[ply_str]
                    main_view.dict_find_2_ply[previously_matched_key] = None
                    break

        main_view.dict_ply_2_find[ply_str] = find_str

    def remove_match(self):
        """This function creates a pop up box that asks if the user wants to remove the match"""
        _, main_view, main_presenter = self.get_model_view_presenter()
        # Get the info to be displayed in the alert
        find_num = main_view.selected_find.text()
        batch_num = main_view.current_batch.text()
        piece_num = main_view.current_piece.text()
        year_num = main_view.current_year.text()
        # Setting up the message
        msg = QMessageBox(
            main_view,
            text=(
                f"Remove the match of the Find ({find_num}), which are batch "
                f"({batch_num}) piece ({piece_num}) year ({year_num}). Proceed?"
            ),
        )
        # Set up the handler for the OK button
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(main_presenter.remove_match_confirm)
        # Show the message
        msg.exec()

    def remove_match_confirm(self, e):
        """This function will try to remove an existent match

        Args:
            e (button): _description_
        """

        # If the button clicked is not ok, we do not remove the match
        if e.text() != "OK":
            return
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        selected_item = main_view.finds_list.currentItem()
        # We will only consider removing the match if the selected item is not none or ""
        if not selected_item:
            return

        # Get the previous year, batch and piece
        previous_current_batch_num = main_view.current_batch.text()
        previous_current_piece_num = main_view.current_piece.text()
        previous_current_year = main_view.current_year.text()

        # In case there is no a 3d model matched before with this find, we don't have
        # to remove it at all
        if not batch_piece_year_valid(
            previous_current_batch_num,
            previous_current_piece_num,
            previous_current_year,
        ):
            return

        # Now all things are set. We can get the info needed to update the database
        (
            easting,
            northing,
            context,
        ) = main_presenter.get_easting_northing_context()
        find = selected_item.text()

        # We update the database to indicate we are unmatching a find with its 3d model
        main_model.update_match_info(easting, northing, context, find, None, None, None)
        # We blacken the item in the find list to indicate that
        selected_item.setForeground(QColor("black"))

        # We go through the unsorted model list and if it is the previous matched item,
        # we blacken it.
        mod = main_view.modelList.model()
        for i in range(mod.rowCount()):
            for j in range(mod.item(i).rowCount()):
                for k in range(mod.item(i).child(j).rowCount()):
                    if (
                        int(previous_current_year) == int(mod.item(i).text())
                        and int(previous_current_batch_num)
                        == int(mod.item(i).child(j).text())
                        and int(previous_current_piece_num)
                        == int(mod.item(i).child(j).child(k).text())
                    ):
                        # Make the old selected black
                        mod.item(i).child(j).child(k).setForeground(QColor("black"))

        # We go through the sorted model list and if it is the previous matched item, we blacken it.
        sorted_mod = main_view.sorted_model_list.model()
        for i in range(sorted_mod.rowCount()):
            if sorted_mod.item(i).text() == (
                f"{previous_current_year}, Batch {int(previous_current_batch_num):03},"
                f" model: {int(previous_current_piece_num)}"
            ):
                (sorted_mod.item(i)).setForeground(QColor("black"))

        # We remove the matching from the two dicts so that the application knows they are no
        # longer matched together
        find_str = f"{easting},{northing},{context},{int(find)}"
        ply_str = (
            f"{int(previous_current_year)},{int(previous_current_batch_num)},"
            f"{int(previous_current_piece_num)}"
        )
        main_view.dict_find_2_ply[find_str] = None
        main_view.dict_ply_2_find[ply_str] = None

        # We show on the GUI that we unmatched the 3d model
        main_view.current_batch.setText("NS")
        main_view.current_piece.setText("NS")
        main_view.current_year.setText("NS")
