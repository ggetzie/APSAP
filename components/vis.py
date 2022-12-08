import win32gui
import open3d as o3d
from area_detect import AreaComparator
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import   QWindow 
from PyQt5.QtWidgets import  QWidget
from PyQt5.QtCore import Qt,QTimer
from components.ColorSummary import get_color_difference
from components.boundingSimilarity import get_3d_width_length
import re
MODELS_FILES_DIR = "finds/3dbatch/2022/batch_*/registration_reso1_maskthres242/final_output/piece_*_world.ply"
MODELS_FILES_RE = "finds/3dbatch/2022/batch_(.+?)/registration_reso1_maskthres242/final_output/piece_(.+?)_world.ply"
class Visualized:
 
    def set_up_3d_window(self):
            widget = self.model

            self.vis = o3d.visualization.Visualizer()
            self.vis.create_window(visible=False) #Visible false there wont be an extra window opened
            self.area_comparator = AreaComparator(self.vis)
            hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")


            self.window = QWindow.fromWinId(hwnd)
            self.windowcontainer = QWidget.createWindowContainer(self.window, widget)
            self.windowcontainer.setMinimumSize(430, 390)

            timer = QTimer(self)
            timer.timeout.connect(self.update_vis)
            timer.start(1)
    
    def update_vis(self):

                self.vis.poll_events()
                self.vis.update_renderer()

    def change_model(self,current_pcd, previous_pcd):
        self.vis.get_render_option().point_size = 5#Generally we need this value to be larger only if we draw the jpgs
        if previous_pcd :
            self.vis.remove_geometry(previous_pcd)
        self.current_pcd = current_pcd
        self.vis.add_geometry(current_pcd)
        self.vis.update_geometry(current_pcd)

    def change_3d_model(self, current, previous):
        current_model_path = (current.data( Qt.UserRole))

        if current_model_path:
            self.path_3d_model = current_model_path
            current_pcd_load = o3d.io.read_point_cloud(current_model_path)
            if not hasattr(self, "current_pcd"):
                self.current_pcd = None
            self.change_model( current_pcd_load, self.current_pcd)
            self.current_pcd = current_pcd_load
            
            m = re.search( MODELS_FILES_RE, current_model_path.replace("\\", "/"))
                #This error happens when the relative path is different
            if m:
                    
                batch_num = str(int(m.group(1))) # int("006") -> int(6). We remove leading 0
                piece_num = m.group(2)
                self.new_batch.setText(batch_num)
                self.new_piece.setText(piece_num)
                    
 