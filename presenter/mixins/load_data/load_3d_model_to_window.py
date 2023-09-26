import open3d as o3d
from PyQt5.QtCore import Qt


class Load3dModelToWindowMixin:
    """This mixin is about "Loading 3d model into the ply Window"
    """    

    def clean_ply_window(self):
        """This function removes any existent 3d model in the ply window 

        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
      
        main_view.current_pcd = None
        main_view.ply_window.clear_geometries()
        
    def change_3d_model(self, current):
        """This function changes the 3d model currently displayed in the ply window

        Args:
            current (object): The current selected item in the 3d model
        """        
        main_model, main_view, main_presenter = self.get_model_view_presenter()
        #Get the saved path in the selected item
        current_model_path = current.data(Qt.UserRole)
        #If the path exists, we try to read it and display it 
        if current_model_path:
          
                #Load the 3d model and set the scene
                current_pcd_load = o3d.io.read_point_cloud(current_model_path)
                main_view.ply_window.get_render_option().point_size = 5  
                #If there is a 3d model previously, we remove it
                main_presenter.clean_ply_window()
                #We add the 3d model and display it.
                main_view.current_pcd = current_pcd_load
                main_view.ply_window.add_geometry(main_view.current_pcd )
                main_view.ply_window.update_geometry(main_view.current_pcd )

                #We get the 3d model's information (year, batch, piece number) and display them
                (year, batch, piece)  = main_presenter.get_year_batch_piece(current_model_path)
                main_view.new_year.setText(year)
                main_view.new_batch.setText(str(int(batch)))
                main_view.new_piece.setText(piece)
            