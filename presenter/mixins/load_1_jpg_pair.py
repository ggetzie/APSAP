from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PIL.ImageQt import ImageQt
import open3d as o3d
import time

class Load1jpgPairMixin:  # bridging the view(gui) and the model(data)

    def load_find_images(self, selected_item):

        main_model, main_view, main_presenter = self.get_model_view_presenter()
        main_view.selected_find_widget = selected_item
        #Setting the images to be shown
        try:
            find_num = main_view.finds_list.currentItem().text()

        except AttributeError:
            main_view.findFrontPhoto_l.clear()
            main_view.findBackPhoto_l.clear()
            return

        photos_dir = (
            main_presenter.get_context_dir()
            / main_model.path_variables["FINDS_SUBDIR"]
            / find_num
            / main_model.path_variables["FINDS_PHOTO_DIR"]
        )

        main_view.path_2d_picture = photos_dir
       
        front_photo = ImageQt(
            main_model.open_image(str(photos_dir / "1.jpg"), full_size=False)
        )
        back_photo = ImageQt(
            main_model.open_image(str(photos_dir / "2.jpg"), full_size=False)
        )
      
        main_view.findFrontPhoto_l.setPixmap(
            QPixmap.fromImage(front_photo).scaledToWidth(
                main_view.findFrontPhoto_l.width()
            )
        )
        main_view.current_image_front = str(photos_dir / "1.jpg")

        main_view.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(
                main_view.findBackPhoto_l.width()
            )
        )
        main_view.current_image_back= str(photos_dir / "2.jpg")
        main_view.selected_find.setText(find_num)
        easting_northing_context = main_presenter.get_easting_northing_context()

        

        _3d_locations = main_view._3d_model_dict[
            f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"
        ]
        find_str = f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"
        
         
         
        #Loading the 3d model already matched before
        if  find_str in main_view.dict_find_2_ply and main_view.dict_find_2_ply[find_str] != None:#_3d_locations[0] != None and _3d_locations[1] != None:
            ply_str = main_view.dict_find_2_ply[find_str] 
            (batch_year, batch_num, batch_piece) = ply_str.split(",")
            main_view.current_year.setText(str(batch_year))
            main_view.current_batch.setText(str(batch_num))
            main_view.current_piece.setText(str(batch_piece))
            path = str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
            whole_path = path.replace("*", f"{int(batch_num):03}", 1).replace(
                "*", f"{int(batch_piece)}", 1
            )
            now = time.time()
            current_pcd_load = o3d.io.read_point_cloud(whole_path, remove_nan_points=True, remove_infinite_points=True)
            if hasattr(main_view, "current_pcd"):

                main_presenter.change_model(current_pcd_load, main_view.current_pcd)
            else:
                main_presenter.change_model(current_pcd_load, None)
 
        else:
            main_view.current_year.setText("NS")
            main_view.current_batch.setText("NS")
            main_view.current_piece.setText("NS")
            if hasattr(main_view, "current_pcd"):
                main_view.ply_window.remove_geometry(main_view.current_pcd)
                main_view.current_pcd = None

 
        _2d_image_path = photos_dir
        #Generate a list of 3d models sorted by similarity. 
  
   
        flat_simllarity_list = main_presenter.genereate_similiarity_ranked_pieces(
            main_presenter.get_similaritiy_scores(
             _2d_image_path
        )
        )
        #Generate a dictionary to mark if a certain 3d model is matched to other images already
        #This dictionary will be used in the later stage, when we have to the list item of 3d models already matched before to red
        # all_matched_3d_models = set()
        # for key in main_view._3d_model_dict:
        #     if not (
        #         main_view._3d_model_dict[key][0] == None
        #         and main_view._3d_model_dict[key][1] == None
        #     ):
        #         all_matched_3d_models.add(main_view._3d_model_dict[key])

        model = QStandardItemModel(main_view)
        model.setHorizontalHeaderLabels(["Sorted models"])
        for weighted_mean, batch_num, piece_num, year in (sorted(flat_simllarity_list)):
            
            #In case the filter range is valid, we may have to skip adding the current item to the list
            if main_view.checkValid():
                #We consider the next if batch_number is not  in the range
                if (not (int(batch_num ) >= self.main_view.batch_start.value() and int(batch_num )  <= self.main_view.batch_end.value())):
                    continue
            

            ply = QStandardItem(
                f"Year: {year}, Batch {batch_num}, model: {piece_num}"
            )
            path = str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
            whole_path = path.replace("*", f"{int(batch_num):03}", 1).replace(
                "*", f"{int(piece_num)}", 1
            )

            ply_str = f"{int(year)},{int(batch_num)},{int(piece_num)}"

            
            # if (
            #     int(batch_num),
            #     int(piece_num),
            # ) in all_matched_3d_models:
            if ply_str in main_view.dict_ply_2_find:
                ply.setForeground(QColor("red"))

            ply.setData(f"{whole_path}", Qt.UserRole)

            model.appendRow(ply)

        main_view.sorted_model_list.setModel(model)

        main_view.sorted_model_list.selectionModel().currentChanged.connect(
            main_presenter.change_3d_model
        )
