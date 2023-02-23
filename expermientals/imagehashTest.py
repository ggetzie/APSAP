
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
import matplotlib.pyplot as plt

np.set_printoptions(suppress=True)


from debug_database import get_all_pottery_sherd_info



print(len(get_all_pottery_sherd_info()))
def get_lumance_summary_2d(img_path):
    pic_f_image = Image.open(img_path).resize((450, 300), Image.LANCZOS)
    ceremicsmask_predictor = MaskPredictor("../computation/ceremicsmask.pt")
    #Getting the numpy arrys for the image and the mask
    img_mask_np = np.array(ceremicsmask_predictor.predict(pic_f_image))
    img_np = np.array(pic_f_image.convert('RGBA'))
    #Cleaning the background
    for i in range(len(img_mask_np)):
        for j in range(len(img_mask_np[0])):
           if img_mask_np[i][j]  <= 170:
                img_np[i][j][0] = 0
                img_np[i][j][1] = 0
                img_np[i][j][2] = 0
                img_np[i][j][3] = 0
    image =   Image.fromarray((img_np))

    np_image =np.array(image.convert('L')).ravel()
    
    #gather lumance summary
    lumance_summary = []
 
    for i in range(0, 256):
        lumance_summary.append(0)
    for luminance in np_image:
        if luminance != 0:
            lumance_summary[luminance] += 1
 
 
    return lumance_summary


def get_lumance_summary_3d(model_path):
    ply_window = o3d.visualization.Visualizer()

    ply_window.create_window(visible=False, width=430, height=390)   
    ply_window.get_render_option().light_on = False
    #load the model
    current_pcd_load = o3d.io.read_point_cloud(model_path) 
    ply_window.add_geometry(current_pcd_load)
    ctr = ply_window.get_view_control()    
    ply_window.get_render_option().point_size = 5
    ctr.change_field_of_view(step=-9)

    img_captured = ply_window.capture_screen_float_buffer(True)
    image_np =  np.multiply(np.array(img_captured), 255).astype(np.uint8)
    img = Image.fromarray(image_np)
    
    img_np = np.array(img.convert('RGBA'))
    
    for i in range(len(img_np)):
        for j in range(len(img_np[0])):
           if img_np[i][j][0]  == 255 and img_np[i][j][1]  == 255 and img_np[i][j][2]  == 255:
                img_np[i][j][0] = 0
                img_np[i][j][1] = 0
                img_np[i][j][2] = 0
                img_np[i][j][3] = 0
    image =   Image.fromarray((img_np))
 
    np_image = np.array(image.convert('L')).ravel()
    print(len(np_image))
    

    #clean up the model

    ply_window.remove_geometry(current_pcd_load)
    del ctr

    #generate the summary and return the result
 
    
    #gather lumance summary
    lumance_summary = []
    for i in range(0, 256):
        lumance_summary.append(0)
    for luminance in np_image:
        if luminance != 0:
            lumance_summary[luminance] += 1
    return lumance_summary
import json
"""
all_images_urls = []
ceremicsmask_predictor = MaskPredictor("../computation/ceremicsmask.pt")
"""
model_path = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\3dbatch\2022\batch_000\registration_reso1_maskthres242\final_output\piece_1_world.ply"

img_path = r"D:\ararat\data\files\N\38\478020\4419550\11\finds\individual\1\photos\1.jpg"
"""
_3d_summa = get_lumance_summary_3d(model_path)
_2d_summa = get_lumance_summary_2d(img_path)
 
normalized_3d_summa = (np.array(_3d_summa)/sum(_3d_summa))

normalized_2d_summa = (np.array(_2d_summa)/sum(_2d_summa))

#Now since all numbers are like to be fraction, like 0.02, 0.314, it would be good if we can normalized them between 0 and 1 
min_3d = min(normalized_3d_summa)
max_3d = max(normalized_3d_summa)

min_2d = min(normalized_2d_summa)
max_2d = max(normalized_2d_summa)

print((normalized_3d_summa - min_3d)/(max_3d - min_3d))
print((normalized_2d_summa - min_2d)/(max_2d - min_2d))
"""


my_file = "./allShardsData.json"
import json
  
# Opening JSON file
f = open(my_file)
  
 
data = json.load(f)
 
kc = {'4780204419550', '4781304419430', '4782304419460'}
rows = []

packed_2d_3d = []

for row in data:
    if(row[-3] != None and row[-2]!= None):
        hemisphere = row[0]
        zone = row[1]
        easting = row[2]
        northing = row[3]
        trench = row[4]
        piece_2d = row[5]
        batch = row[-3]
        piece_3d = row[-2]
        img_1 =  rf"D:\ararat\data\files\{hemisphere}\{zone}\{easting}\{northing}\{trench}\finds\individual\{piece_2d}\photos\1.jpg"
       
        img_2 =  rf"D:\ararat\data\files\{hemisphere}\{zone}\{easting}\{northing}\{trench}\finds\individual\{piece_2d}\photos\2.jpg"
         
        model_path = rf"D:\ararat\data\files\{hemisphere}\{zone}\{easting}\{northing}\{trench}\finds\3dbatch\2022\batch_{int(batch):03}\registration_reso1_maskthres242\final_output\piece_{piece_3d}_world.ply"
        if Path(img_1).is_file() and Path(img_2).is_file() and Path(model_path).is_file():
            packed ={
                "img_1": img_1,
                "img_2": img_2,
                "model" : model_path
            }
            packed_2d_3d.append(packed)

import json
with open('matched.json', 'w') as f:
    json.dump(packed_2d_3d, f)
import time

summaries_rows = []
for item in packed_2d_3d:
    print()
    print(f"Handling: {item} now!")
    now = time.time()
    summaries = {

    "img_1": item["img_1"],

    "img_2": item["img_2"],
    "model": item["model"],
    "img_1_summa": get_lumance_summary_2d(item["img_1"]),
    "img_2_summa" : get_lumance_summary_2d(item["img_2"]),
    "model_summa" : get_lumance_summary_3d(item["model"])
    }
    summaries_rows.append(summaries)
    print(f"It takes {time.time() - now} seconds for this row")
    print(summaries)
    print()
with open('summaries.json', 'w') as f:
    json.dump(summaries_rows, f)
print("Saving the result")