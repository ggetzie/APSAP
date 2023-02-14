from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox


class AddAndRemoveMatchMixin:  # bridging the view(gui) and the model(data)

    def remove_match(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        # This functions removes the match between the image and the 3d model
        selected_item = main_view.finds_list.currentItem()

        # Only remove model when an image is selected
        if selected_item:
            num = selected_item.text()
            selected_item.setForeground(QColor("black"))
            # Update the database
            (
                easting,
                northing,
                context,
            ) = main_presenter.get_easting_northing_context()
            main_model.update_match_info(easting, northing, context, num, None, None)
            # Unred the matched items in the 3d models list
            previous_current_batch_num = main_view.current_batch.text()
            previous_current_piece_num = main_view.current_piece.text()

            mod = main_view.modelList.model()
            # Make the item Black in modelList
            for i in range(mod.rowCount()):
                for j in range(mod.item(i).rowCount()):
                    if (
                        previous_current_batch_num != "NS"
                        and previous_current_piece_num != "NS"
                    ):
                        if int(previous_current_batch_num) == int(
                            mod.item(i).text()
                        ) and int(previous_current_piece_num) == int(
                            mod.item(i).child(j).text()
                        ):
                            # Make the old selected black
                            mod.item(i).child(j).setForeground(QColor("black"))
            # Make the item Black in model sorted list
            sorted_mod = main_view.sorted_model_list.model()
            for i in range(sorted_mod.rowCount()):

                if (
                    previous_current_batch_num != "NS"
                    and previous_current_piece_num != "NS"
                ):

                    if (
                        sorted_mod.item(i).text()
                        == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                    ):

                        (sorted_mod.item(i)).setForeground(QColor("black"))
            # Also we need to unred the previous selected item in the sorted model list

            # Remove the dict entry from
            dict_key = f"{easting},{northing },{context},{int(num)}"
            main_view._3d_model_dict[dict_key] = (None, None)
            main_view.current_batch.setText(f"NS")
            main_view.current_piece.setText(f"NS")

    def add_match_confirm(self, e):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if e.text() == "OK":
            easting, northing, context = main_presenter.get_easting_northing_context()
            find_num = main_view.selected_find.text()
            batch_num = main_view.new_batch.text()
            piece_num = main_view.new_piece.text()
            previous_current_batch_num = main_view.current_batch.text()
            previous_current_piece_num = main_view.current_piece.text()

            if (
                easting
                and northing
                and context
                and find_num
                and batch_num
                and piece_num
            ):
                main_model.update_match_info(
                    easting,
                    northing,
                    context,
                    int(find_num),
                    int(batch_num),
                    int(piece_num),
                )
                # Here to avoid loading time, we manually update some data. We can
                # reload the contexts but it would be way too slow

                if hasattr(main_view, "selected_find_widget"):
                    main_view.selected_find_widget.setForeground(QColor("red"))
                main_view.current_batch.setText(batch_num)
                main_view.current_piece.setText(piece_num)
                # Here's let's try to get color red

                mod = main_view.modelList.model()
                # Make the item red in modelList
                for i in range(mod.rowCount()):

                    for j in range(mod.item(i).rowCount()):
                        if int(batch_num) == int(mod.item(i).text()) and int(
                            piece_num
                        ) == int(mod.item(i).child(j).text()):
                            # Make the newly selected red
                            mod.item(i).child(j).setForeground(QColor("red"))
                        if (
                            previous_current_batch_num != "NS"
                            and previous_current_piece_num != "NS"
                        ):
                            if int(previous_current_batch_num) == int(
                                mod.item(i).text()
                            ) and int(previous_current_piece_num) == int(
                                mod.item(i).child(j).text()
                            ):
                                # Make the old selected black
                                mod.item(i).child(j).setForeground(QColor("black"))

                # Make the item red in sorted_model_list
                sorted_mod = main_view.sorted_model_list.model()
                for i in range(sorted_mod.rowCount()):

                    if (
                        sorted_mod.item(i).text()
                        == f"Batch {int(batch_num):03}, model: {int(piece_num)}"
                    ):
                        (sorted_mod.item(i)).setForeground(QColor("red"))
                    if (
                        previous_current_batch_num != "NS"
                        and previous_current_piece_num != "NS"
                    ):
                        if (
                            sorted_mod.item(i).text()
                            == f"Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                        ):
                            (sorted_mod.item(i)).setForeground(QColor("black"))
                # Also we need to unred the previous selected item in the sorted model list

                dict_key = f"{easting},{northing },{context},{int(find_num)}"
                main_view._3d_model_dict[dict_key] = (int(batch_num), int(piece_num))

            else:
                QMessageBox(
                    main_view, text="Please select both a find and a model"
                ).exec()

    def add_match(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        find_num = main_view.selected_find.text()
        batch_num = main_view.new_batch.text()
        piece_num = main_view.new_piece.text()
        msg = QMessageBox(main_view, text=f"Update Find ({find_num}) to batch ({batch_num}) piece ({piece_num}). Proceed?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(main_presenter.add_match_confirm)
        msg.exec()
