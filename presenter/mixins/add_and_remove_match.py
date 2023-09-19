from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox


class AddAndRemoveMatchMixin:  # bridging the view(gui) and the model(data)

    def remove_match(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        
        selected_item = main_view.finds_list.currentItem()

        if selected_item:
            find = selected_item.text()
            selected_item.setForeground(QColor("black"))
            # Update the database
            (
                easting,
                northing,
                context,
            ) = main_presenter.get_easting_northing_context()
           
            # Unred the matched items in the 3d models list
            previous_current_batch_num = main_view.current_batch.text()
            previous_current_piece_num = main_view.current_piece.text()
            previous_current_year = main_view.current_year.text()

            mod = main_view.modelList.model()
            # Make the item Black in modelList
            if (
                previous_current_batch_num != None
                and previous_current_piece_num != None
                and previous_current_year != None
                and previous_current_batch_num != "NS"
                and previous_current_piece_num != "NS"
                and previous_current_year != "NS"
            ):
                main_model.update_match_info(easting, northing, context, find, None, None, None)
                for i in range(mod.rowCount()):
                    for j in range(mod.item(i).rowCount()):
                        for k in range(mod.item(i).child(j).rowCount()):
                            if int(previous_current_year) == int(
                                mod.item(i).text()
                            ) and int(previous_current_batch_num) == int(
                                mod.item(i).child(j).text()
                            )and int(previous_current_piece_num) == int(
                                mod.item(i).child(j).child(k).text()
                            ):
                                # Make the old selected black
                                mod.item(i).child(j).child(k).setForeground(QColor("black"))
                # Make the item Black in model sorted list
                sorted_mod = main_view.sorted_model_list.model()
               
                for i in range(sorted_mod.rowCount()):
                    if (
                        sorted_mod.item(i).text()
                        == f"{previous_current_year}, Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                    ):

                        (sorted_mod.item(i)).setForeground(QColor("black"))
                # Also we need to unred the previous selected item in the sorted model list

                # Remove the dict entry from
                dict_key = f"{easting},{northing },{context},{int(find)}"
                batch_year = previous_current_year
                batch_num = previous_current_batch_num
                batch_piece = previous_current_piece_num
                find_str = f"{easting},{northing},{context},{int(find)}"
                ply_str = f"{int(batch_year)},{int(batch_num)},{int(batch_piece)}"
                main_view.dict_find_2_ply[find_str] = None
                main_view.dict_ply_2_find[ply_str] = None


                main_view.current_batch.setText(f"NS")
                main_view.current_piece.setText(f"NS")
                main_view.current_year.setText(f"NS")
    def add_match_confirm(self, e):
        main_model, main_view, main_presenter = self.get_model_view_presenter()

        if e.text() == "OK":
            easting, northing, context = main_presenter.get_easting_northing_context()
            find_num = main_view.selected_find.text()
            batch_num = main_view.new_batch.text()
            piece_num = main_view.new_piece.text()
            new_year = main_view.new_year.text()

            previous_current_batch_num = main_view.current_batch.text()
            previous_current_piece_num = main_view.current_piece.text()
            previous_current_year = main_view.current_year.text()

            if (
                easting != None
                and northing != None
                and context != None
                and find_num != None
                and batch_num != None
                and piece_num != None
                and new_year != None and new_year.isnumeric()
            ):
                main_model.update_match_info(
                    easting,
                    northing,
                    context,
                    find_num,
                    batch_num,
                    piece_num,
                    new_year
                )
                from pathlib import Path
                #Here we reconstruct the path
                path = str(
                    (
                        main_presenter.get_context_dir()
                        / main_model.path_variables["MODELS_FILES_DIR"]
                    )
                )
                print(f"path: {path}")
                original_ply = path.replace("*",str(new_year), 1).replace("*", f"{int(batch_num):03}", 1).replace(
                "*", f"{int(piece_num)}", 1
                )
                 
                mesh_ply = (original_ply[:-4] + "_sample0_3_mesh.ply")
                context_dir = main_presenter.get_context_dir()
                finds_subdir = main_model.path_variables["FINDS_SUBDIR"]
                folder = context_dir / finds_subdir / str(find_num) / "3d" /  "gp"
                
                original_destination = Path(folder/"a.ply")
                mesh_destination = Path(folder/"a_0_3_mesh.ply")

                print(f"original_ply location: {original_ply}")
                print()
                print(f"mesh_ply location: {mesh_ply}")
                print()
                print(f"original_ply destination: {original_destination}")
                print()
                print(f"mesh_ply destination {mesh_destination}")
                print()
                print(f"Copying file from {original_ply} to {original_destination}")
                main_model.fixAndCopyPly(str(Path(original_ply)), str(Path(original_destination)))
                print(f"Copying file from {mesh_ply} to {mesh_destination}")
                main_model.fixAndCopyPly(str(Path(mesh_ply)), str(Path(mesh_destination)))
                # piece_1_world_sample0_3_mesh
             

                # Here to avoid loading time, we manually update some data. We can
                # reload the contexts but it would be way too slow

                if hasattr(main_view, "selected_find_widget"):
                    main_view.selected_find_widget.setForeground(QColor("red"))
                main_view.current_batch.setText(batch_num)
                main_view.current_piece.setText(piece_num)                
                main_view.current_year.setText(new_year)

                # Here's let's try to get color red

                mod = main_view.modelList.model()
                # Make the item red in modelList
                
                for i in range(mod.rowCount()):

                    for j in range(mod.item(i).rowCount()):
                        
                        for k in range(mod.item(i).child(j).rowCount()):
                            if (
                                previous_current_batch_num != None
                                and previous_current_piece_num != None
                                and previous_current_year != None
                                and previous_current_batch_num != "NS"
                                and previous_current_piece_num != "NS"
                                and previous_current_year != "NS"
                            ):
                                if int(previous_current_year) == int(
                                    mod.item(i).text()
                                ) and int(previous_current_batch_num) == int(
                                    mod.item(i).child(j).text()
                                ) and int(previous_current_piece_num) == int(
                                    mod.item(i).child(j).child(k).text()
                                ):
                                    # Make the old selected black
                                    mod.item(i).child(j).child(k).setForeground(QColor("black"))
                            if int(new_year) == int(mod.item(i).text()
                            ) and int(batch_num) == int(mod.item(i).child(j).text()
                            ) and int(piece_num) == int(mod.item(i).child(j).child(k).text()):
                                                        # Make the newly selected red
                                mod.item(i).child(j).child(k).setForeground(QColor("red"))

                # Make the item red in sorted_model_list
                sorted_mod = main_view.sorted_model_list.model()
                for i in range(sorted_mod.rowCount()):
                    

                    if (
                            previous_current_batch_num != None
                            and previous_current_piece_num != None
                            and previous_current_year != None
                            and previous_current_batch_num != "NS"
                            and previous_current_piece_num != "NS"
                            and previous_current_year != "NS"
                    ):
                        if (
                            sorted_mod.item(i).text()
                            == f"{previous_current_year}, Batch {int(previous_current_batch_num):03}, model: {int(previous_current_piece_num)}"
                        ):
                            (sorted_mod.item(i)).setForeground(QColor("black"))
                    if (
                        sorted_mod.item(i).text()
                        == f"{new_year}, Batch {int(batch_num):03}, model: {int(piece_num)}"
                    ):
                        (sorted_mod.item(i)).setForeground(QColor("red"))
                # Also we need to unred the previous selected item in the sorted model list

                dict_key = f"{easting},{northing },{context},{int(find_num)}"
                batch_year = new_year
                batch_num = batch_num
                batch_piece = piece_num
                find_str = f"{easting},{northing},{context},{int(find_num)}"
                ply_str = f"{int(batch_year)},{int(batch_num)},{int(batch_piece)}"
                main_view.dict_find_2_ply[find_str] = ply_str
                main_view.dict_ply_2_find[ply_str] = find_str

            else:
                QMessageBox(
                    main_view, text="Please select both a find and a model"
                ).exec()
    # next step: use the triple 
    def add_match(self):
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        find_num = main_view.selected_find.text()
        batch_num = main_view.new_batch.text()
        piece_num = main_view.new_piece.text()
        msg = QMessageBox(main_view, text=f"Update Find ({find_num}) to batch ({batch_num}) piece ({piece_num}). Proceed?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.buttonClicked.connect(main_presenter.add_match_confirm)
        msg.exec()
