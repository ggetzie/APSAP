import ctypes

opengl_path = "../computation/opengl32.dll"
ctypes.cdll.LoadLibrary(opengl_path)
import open3d as o3d
import numpy as np
from PIL import Image
import imagehash
import sys
sys.path.insert(0,'..')
from computation.nn_segmentation import MaskPredictor
def white_to_transparency(img):
    x = np.asarray(img.convert('RGBA')).copy()

    x[:, :, 3] = (255 * (x[:, :, :3] <= 240).any(axis=2)).astype(np.uint8)

    return Image.fromarray(x)


ply_window = o3d.visualization.Visualizer()

ply_window.create_window(visible=False)   
ply_window.get_render_option().light_on = False
model_path = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\3dbatch\2022\batch_000\registration_reso1_maskthres242\final_output\piece_0_world.ply"
current_pcd_load = o3d.io.read_point_cloud(model_path) 

ply_window.add_geometry(current_pcd_load)

ctr = ply_window.get_view_control()    

ply_window.get_render_option().point_size = 5
ctr.change_field_of_view(step=-9)

object_image = ply_window.capture_screen_float_buffer(True)
pic =   white_to_transparency( Image.fromarray(np.multiply(np.array(object_image), 255).astype(np.uint8)).resize((450, 300), Image.LANCZOS))
pic.save("here.png")
print(imagehash.average_hash(pic))


pic_front = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\individual\1\photos\1.jpg"
back_front = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\individual\1\photos\2.jpg"



pic_f_image = Image.open(pic_front).resize((450, 300), Image.LANCZOS)
 
ceremicsmask_predictor = MaskPredictor("../computation/ceremicsmask.pt")

mask_image_np = np.array(ceremicsmask_predictor.predict(pic_f_image))


def get_transparent_background_sherd(img, img_mask):

    img_np = np.array(img.convert('RGBA'))
    img_mask_np = np.array(img_mask)
    for i in range(len(img_mask_np)):
        for j in range(len(img_mask_np[0])):
           if img_mask_np[i][j]  <= 170:
                img_np[i][j][0] = 0
                img_np[i][j][1] = 0
                img_np[i][j][2] = 0
                img_np[i][j][3] = 0
    return Image.fromarray(img_np)
img1 = (get_transparent_background_sherd(pic_f_image, mask_image_np))#.save("pic_f_image.png")
print(imagehash.average_hash(img1))

 



pic_b_image = Image.open(back_front).resize((450, 300), Image.LANCZOS)

mask_image_np_b = np.array(ceremicsmask_predictor.predict(pic_b_image))
img2 = (get_transparent_background_sherd(pic_b_image, mask_image_np_b))#.save("pic_b_image.png")
print(imagehash.average_hash(img2))

#mask_image.save("pic_f_image.png")
#(white_to_transparency(pic)).save("here.png")
#pic[pic==255] = 0
#ply_window.remove_geometry(current_pcd_load)

#del ctr
#ply_window.destroy_window()