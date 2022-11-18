import numpy as np
from PIL import Image, ImageStat
import cv2

from matplotlib import pyplot as plt


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

def rotate_image(img, gridPredictor, cermics_predictor):
    ceremic_np = np.array((cermics_predictor.predict(img)))
    grid_np = np.array((gridPredictor.predict(img)))
    ceremic_x = []
    grid_x = []
    for i in range(len(ceremic_np)):
        for j in range(len(ceremic_np[0])):
            if ceremic_np[i, j]:
                ceremic_x.append(j)
            if grid_np[i, j]:
                grid_x.append(j)
    grid_x.sort()
    ceremic_x.sort()
    #Finally have the avg x values for comparing 
    grid_avg_x = (grid_x[int(len(grid_x)/2)])
    ceremic_avg_x = (ceremic_x[int(len(ceremic_x)/2)])
        
    if ceremic_avg_x <= grid_avg_x:
        img = img.rotate(180)
    return img

def mean(li):
    total = 0
    for i in li:
        total += i 
    return total/len(li)

def fig2img(fig):
    """Convert a Matplotlib figure to a PIL Image and return it"""
    import io
    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img