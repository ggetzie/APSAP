import cv2
import numpy as np
from PIL import Image


def get_features(image: Image.Image):

    sift = cv2.SIFT_create()
    cv2_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    keypoints, descriptors = sift.detectAndCompute(cv2_image, None)
    return keypoints, descriptors


def serialize_keypoints(keypoints):
    return [
        (kp.pt, kp.size, kp.angle, kp.response, kp.octave, kp.class_id)
        for kp in keypoints
    ]


def deserialize_keypoints(serialized_keypoints):
    return [
        cv2.KeyPoint(
            x=pt[0][0],
            y=pt[0][1],
            size=pt[1],
            angle=pt[2],
            response=pt[3],
            octave=pt[4],
            class_id=pt[5],
        )
        for pt in serialized_keypoints
    ]
