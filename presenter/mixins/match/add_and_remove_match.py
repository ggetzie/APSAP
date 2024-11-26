# def batch_piece_year_valid(batch_num, piece_num, year):
#     """This function checks if the piece number and year are valid

#     Args:
#         num_piece (str): The piece number
#         year (str): The year

#     Returns:
#         bool: True if the piece number and year are valid, False otherwise
#     """
#     return all(x is not None and x != "NS" for x in [batch_num, piece_num, year])


class AddAndRemoveMatchMixin:
    """This class contains the functions that handle modifying an entry at the database.
    Notice that we need confirmation before the database operations are being done to make
    it more secure
    """

    # def remove_match(self):
    #     """This function creates a pop up box that asks if the user wants to remove the match"""
    #     _, main_view, main_presenter = self.get_model_view_presenter()
    #     # Get the info to be displayed in the alert
    #     find_num = main_view.selected_find.text()
    #     batch_num = main_view.current_batch.text()
    #     piece_num = main_view.current_piece.text()
    #     year_num = main_view.current_year.text()
    #     # Setting up the message
    #     msg = QMessageBox(
    #         main_view,
    #         text=(
    #             f"Remove the match of the Find ({find_num}), which are batch "
    #             f"({batch_num}) piece ({piece_num}) year ({year_num}). Proceed?"
    #         ),
    #     )
    #     # Set up the handler for the OK button
    #     msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    #     msg.buttonClicked.connect(main_presenter.remove_match_confirm)
    #     # Show the message
    #     msg.exec()

    # def remove_match_confirm(self, e):
    #     """This function will try to remove an existent match

    #     Args:
    #         e (button): _description_
    #     """

    #     # If the button clicked is not ok, we do not remove the match
    #     if e.text() != "OK":
    #         return
    #     main_model, main_view, main_presenter = self.get_model_view_presenter()

    #     selected_item = main_view.finds_list.currentItem()
    #     # We will only consider removing the match if the selected item is not none or ""
    #     if not selected_item:
    #         return

    #     # Get the previous year, batch and piece
    #     previous_current_batch_num = main_view.current_batch.text()
    #     previous_current_piece_num = main_view.current_piece.text()
    #     previous_current_year = main_view.current_year.text()

    #     # In case there is no a 3d model matched before with this find, we don't have
    #     # to remove it at all
    #     if not batch_piece_year_valid(
    #         previous_current_batch_num,
    #         previous_current_piece_num,
    #         previous_current_year,
    #     ):
    #         return

    #     # Now all things are set. We can get the info needed to update the database
    #     (
    #         easting,
    #         northing,
    #         context,
    #     ) = main_presenter.get_easting_northing_context()
    #     find = selected_item.text()

    #     # We update the database to indicate we are unmatching a find with its 3d model
    #     main_model.update_match_info(easting, northing, context, find, None, None, None)
    #     # We blacken the item in the find list to indicate that
    #     selected_item.setForeground(QColor("black"))

    #     # We go through the unsorted model list and if it is the previous matched item,
    #     # we blacken it.
    #     mod = main_view.unsorted_model_list.model()
    #     for i in range(mod.rowCount()):
    #         for j in range(mod.item(i).rowCount()):
    #             for k in range(mod.item(i).child(j).rowCount()):
    #                 if (
    #                     int(previous_current_year) == int(mod.item(i).text())
    #                     and int(previous_current_batch_num)
    #                     == int(mod.item(i).child(j).text())
    #                     and int(previous_current_piece_num)
    #                     == int(mod.item(i).child(j).child(k).text())
    #                 ):
    #                     # Make the old selected black
    #                     mod.item(i).child(j).child(k).setForeground(QColor("black"))

    #     # We go through the sorted model list and if it is the previous matched item, we blacken it.
    #     sorted_mod = main_view.sorted_model_list.model()
    #     for i in range(sorted_mod.rowCount()):
    #         if sorted_mod.item(i).text() == (
    #             f"{previous_current_year}, Batch {int(previous_current_batch_num):03},"
    #             f" model: {int(previous_current_piece_num)}"
    #         ):
    #             (sorted_mod.item(i)).setForeground(QColor("black"))

    #     # We remove the matching from the two dicts so that the application knows they are no
    #     # longer matched together
    #     find_str = f"{easting},{northing},{context},{int(find)}"
    #     ply_str = (
    #         f"{int(previous_current_year)},{int(previous_current_batch_num)},"
    #         f"{int(previous_current_piece_num)}"
    #     )
    #     main_view.dict_find_2_ply[find_str] = None
    #     main_view.dict_ply_2_find[ply_str] = None

    #     # We show on the GUI that we unmatched the 3d model
    #     main_view.current_batch.setText("NS")
    #     main_view.current_piece.setText("NS")
    #     main_view.current_year.setText("NS")
