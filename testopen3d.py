import open3d as o3d
 

ply_window = o3d.visualization.Visualizer()
import time
now = time.time()
ply_window.create_window(visible=True)   
print(f"{time.time() - now} seconds have passed")