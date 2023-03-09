from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QStandardItem, QStandardItemModel
from PIL.ImageQt import ImageQt
import open3d as o3d
import time

class Load1jpgPairMixin:  # bridging the view(gui) and the model(data)

    def load_find_images(self, selected_item):

        main_model, main_view, main_presenter = self.get_model_view_presenter()
        now  = time.time()
        main_view.selected_find_widget = selected_item
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
        
        main_view.findBackPhoto_l.setPixmap(
            QPixmap.fromImage(back_photo).scaledToWidth(
                main_view.findBackPhoto_l.width()
            )
        )
        print(f"{time.time() - now} seconds have passed for setting picture")
        main_view.selected_find.setText(find_num)
        easting_northing_context = main_presenter.get_easting_northing_context()
        _3d_locations = main_view._3d_model_dict[
            f"{easting_northing_context[0]},{easting_northing_context[1]},{easting_northing_context[2]},{int(find_num)}"
        ]

        if _3d_locations[0] != None and _3d_locations[1] != None:
            main_view.current_batch.setText(str(_3d_locations[0]))
            main_view.current_piece.setText(str(_3d_locations[1]))
            path = str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
            whole_path = path.replace("*", f"{int(_3d_locations[0]):03}", 1).replace(
                "*", f"{int(_3d_locations[1])}", 1
            )
            current_pcd_load = o3d.io.read_point_cloud(whole_path)
            if hasattr(main_view, "current_pcd"):
                main_presenter.change_model(current_pcd_load, main_view.current_pcd)
            else:
                main_presenter.change_model(current_pcd_load, None)
        else:
            main_view.current_batch.setText("NS")
            main_view.current_piece.setText("NS")
            if hasattr(main_view, "current_pcd"):
                main_view.ply_window.remove_geometry(main_view.current_pcd)
                main_view.current_pcd = None

        print(f"{time.time() - now} seconds have passed for loading ply and miscs")

        _2d_image_path = photos_dir
      
 
        old_flat_similairy_list = []
        flat_simllarity_list = main_presenter.get_similaritiy_scores(
             _2d_image_path
        )
     
        flat_simllarity_list = main_presenter.genereate_similiarity_ranked_pieces(
            flat_simllarity_list
        )
        
        all_matched_3d_models = set()
        for key in main_view._3d_model_dict:
            if not (
                main_view._3d_model_dict[key][0] == None
                and main_view._3d_model_dict[key][1] == None
            ):
                all_matched_3d_models.add(main_view._3d_model_dict[key])

        model = QStandardItemModel(main_view)
        model.setHorizontalHeaderLabels(["Sorted models"])
        for i, score_i_j_tuple in enumerate(sorted(flat_simllarity_list)):
            ply = QStandardItem(
                f"Batch {score_i_j_tuple[1]}, model: {score_i_j_tuple[2]}"
            )
            path = str(
                (
                    main_presenter.get_context_dir()
                    / main_model.path_variables["MODELS_FILES_DIR"]
                )
            )
            whole_path = path.replace("*", f"{int(score_i_j_tuple[1]):03}", 1).replace(
                "*", f"{int(score_i_j_tuple[2])}", 1
            )

            if (
                int(score_i_j_tuple[1]),
                int(score_i_j_tuple[2]),
            ) in all_matched_3d_models:

                ply.setForeground(QColor("red"))

            ply.setData(f"{whole_path}", Qt.UserRole)

            model.appendRow(ply)
        print(f"{time.time() - now} seconds have passed for calculuating similarities")

        main_view.sorted_model_list.setModel(model)

        main_view.sorted_model_list.selectionModel().currentChanged.connect(
            main_presenter.change_3d_model
        )
        print(f"{time.time() -  now } seconds have passed.")