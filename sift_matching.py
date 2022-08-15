"""
sift_matching.py
The core function of image matching that compares the target image and match image using SIFT algorithm in opencv
"""

import cv2

def img_compare(query_img, match_img):

    sift = cv2.SIFT_create()
    
    keypoints1, descriptors1 = sift.detectAndCompute(query_img, None)
    keypoints2, descriptors2 = sift.detectAndCompute(match_img, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch (descriptors1, descriptors2,k=2)

    good_matches = []

    for m1, m2 in matches:
        if m1.distance < 0.9*m2.distance:
            good_matches.append([m1])

    #SIFT_matches = cv2.drawMatchesKnn(query_img, keypoints1, match_img, keypoints2, good_matches, None, flags=2)
    return len(good_matches)

#read in all target match files in one list of tuples in (front_path, back_path) format         
def read_context_targets(target_context_path):    
    context_front_list =  [file for file in target_context_path.rglob('*') if file.name == '2d_image_front.png']
    context_back_list =  [file for file in target_context_path.rglob('*') if file.name == '2d_image_back.png']
    
    master_context_targets_space = []

    if len(context_front_list) != len(context_back_list):
        print("the number of front and back target images is not consistent")
    else:      
        for i in range(0, len(context_front_list)):
            master_context_targets_space.append((context_front_list[i],context_back_list[i]))

    return master_context_targets_space 