import numpy as np
from PIL import Image, ImageStat
import cv2
import json


def get_mask_pixel_width(image):
    #Turned the color_grid mask into numpy array
    np_array = (np.array(image))
 
    x_coordiantes_mask = (sorted(np.where(np_array>200)[1]))
    return x_coordiantes_mask[-15] - x_coordiantes_mask[5]

def get_ceremic_area(ceremic_mask, mm_per_pixel):
    #Turn the mask to an array
    ceremic_array = (np.array(ceremic_mask))
    ceremic_pixel = (np.count_nonzero((ceremic_array >=170)))
    # Turn number of pixels(aka pixel area) into area in mm
    mmSquared = (ceremic_pixel * (mm_per_pixel* mm_per_pixel)) 
    # mm to cm
    cmSquared = mmSquared / 100 
    return cmSquared

 
def brighten(img, target_brightness):
        #Can be useful later
        brightness_diff =  int(target_brightness - int(brightness(img)) )
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = (brightness_diff +  img.astype(np.float64)).clip(0,255).astype(np.uint8)       
        brightened_image = Image.fromarray(cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)) 
        return brightened_image
        
def brightness( im ):
    
        stat = ImageStat.Stat(im)
        return stat.mean[0]
     
def open_image(image_path, full_size):
    if full_size == True:
        return  (Image.open(image_path))
    else:
        return  Image.open(image_path).resize((450,300), Image.ANTIALIAS)
    #(Image.fromarray(cv2.cvtColor(cv2.resize((cv2.imread(image_path) ),(450, 300)),cv2.COLOR_BGR2RGB)))


def simple_get_json(json_file):
    f = open(json_file)
    data = json.load(f)
    return data


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
def simple_save_json(json_object, json_file):
    with open(json_file, 'w') as f:
        json.dump(json_object, f, cls=NpEncoder)