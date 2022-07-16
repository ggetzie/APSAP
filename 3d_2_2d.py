import open3d as o3d
import numpy as np
import os 
import copy

#test path for the point cloud 
path = r'C:\Users\Zichen\Desktop\test\piece_0_world.ply'
dir_path = os.path.dirname(os.path.realpath(__file__))

#read the point cloud
pcd = o3d.io.read_point_cloud(path)

# copy and flip the point cloud by rotating around y axis 
pcd_back = copy.deepcopy(pcd) 
R = pcd_back.get_rotation_matrix_from_xyz((0, np.pi, 0))
pcd_back.rotate(R, center=(0,0,0))


#visualize and screenshot the front side
vis = o3d.visualization.Visualizer()
vis.create_window(visible=False)
vis.add_geometry(pcd)
vis.poll_events()
vis.update_renderer()
vis.capture_screen_image(dir_path + '\\2d_image_front.png')
vis.remove_geometry(pcd)


#visualize and screenshot the back side
vis.add_geometry(pcd_back)
vis.poll_events()
vis.update_renderer()
vis.capture_screen_image(dir_path + '\\2d_image_back.png')

vis.destroy_window()
