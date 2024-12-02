import cv2
from model.models import A3DModel, ObjectFind


def get_float_similarity(a, b):
    return abs(a - b) / (a + b + 0.0000000001)


def calculate_similarity(a3dmodel: A3DModel, object_find: ObjectFind) -> float:
    """Calculate the similarity between the 3d model and the object find

    Args:
        a3dmodel (A3DModel): The 3d model
        object_find (ObjectFind): The object find

    Returns:
        similarity_mean: The similarity between the 3d model and the object find
    """
    area_sim = area_similarity(a3dmodel, object_find)
    lw_sim = length_width_similarity(a3dmodel, object_find)
    contour_sim = contour_similarity(a3dmodel, object_find)

    similarity_mean = area_sim * 1.2 + lw_sim * 0.2 + contour_sim * 0.7
    return similarity_mean


def area_similarity(a3dmodel: A3DModel, find: ObjectFind) -> float:
    """Calculate the similarity between the area of the 3d model and the object find

    Args:
        a3dmodel (A3DModel): The 3d model
        find (ObjectFind): The object find

    Returns:
        float: The similarity between the area of the 3d model and the object find
    """
    smaller_area = min(find.area_front, find.area_back)
    larger_area = max(find.area_front, find.area_back)
    return min(
        get_float_similarity(larger_area, a3dmodel.area),
        get_float_similarity(smaller_area, a3dmodel.area),
    )


def length_width_similarity(a3dmodel: A3DModel, find: ObjectFind):
    """Calculate the similarity between the length and width of the 3d model and the object find

    Args:
        a3dmodel (A3DModel): The 3d model
        find (ObjectFind): The object find

    Returns:
        float: The similarity between the length and width of the 3d model and the object find
    """
    similarity_with_img_1 = get_float_similarity(
        find.length_front, a3dmodel.length
    ) + get_float_similarity(find.width_front, a3dmodel.width)

    similarity_with_img_2 = get_float_similarity(
        find.length_back, a3dmodel.length
    ) + get_float_similarity(find.width_back, a3dmodel.width)

    return min(similarity_with_img_1, similarity_with_img_2)


def contour_similarity(a3dmodel: A3DModel, find: ObjectFind):
    """Calculate the similarity between the contour of the 3d model and the object find

    Args:
        a3dmodel (A3DModel): The 3d model
        find (ObjectFind): The object find

    Returns:
        float: The similarity between the contour of the 3d model and the object find
    """
    closeness_1 = cv2.matchShapes(find.contour_front, a3dmodel.contour, 1, 0.0)
    closeness_2 = cv2.matchShapes(find.contour_back, a3dmodel.contour, 1, 0.0)
    sim = min(closeness_1, closeness_2)
    return sim
