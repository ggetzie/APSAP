import logging
import pathlib
import torch
from PIL import Image
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor


import computation.transforms as T

logger = logging.getLogger(__name__)

torch.set_num_threads(8)


def get_transform(train):
    transforms = []
    transforms.append(T.PILToTensor())
    transforms.append(T.ConvertImageDtype(torch.float))
    if train:
        transforms.append(T.RandomHorizontalFlip(0.5))
    return T.Compose(transforms)  # Compose transforms together


def get_model_instance_segmentation(num_classes):
    model = torchvision.models.detection.maskrcnn_resnet50_fpn(weights="DEFAULT")
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    hidden_layer = 256
    model.roi_heads.mask_predictor = MaskRCNNPredictor(
        in_features_mask, hidden_layer, num_classes
    )

    return model


class InvalidMaskType(Exception):
    pass


class ModelNotAvailable(Exception):
    pass


COMPUTATION_PATH = pathlib.Path(__file__).parent.parent.parent / "computation"
MODEL_PATHS = {
    "ceramics": COMPUTATION_PATH / "updated_ceremicsmask.pt",
    "colorgrid": COMPUTATION_PATH / "colorgridmask.pt",
    "colorgrid_24": COMPUTATION_PATH / "Different_colro_grid.pt",
}

if not all([path.exists() for path in MODEL_PATHS.values()]):
    raise ModelNotAvailable(
        f"Model files are not available, please save them in {COMPUTATION_PATH}"
    )


class MaskPredictor:
    def __init__(self, mask_type="ceramics"):
        self.mask_type = mask_type
        try:
            model_path = MODEL_PATHS[mask_type]
        except KeyError as e:
            raise InvalidMaskType(
                f"Invalid mask type {mask_type}, only ceramics and colorgrid, colorgrid_24 are allowed"
            ) from e

        self.device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )
        logger.debug("Loading %s model from %s", mask_type, model_path)

        loaded_model = get_model_instance_segmentation(2)
        if not torch.cuda.is_available():
            logger.debug("CUDA not available, loading model on CPU")
            loaded_model.load_state_dict(
                torch.load(model_path, map_location=torch.device("cpu"))
            )
        else:
            loaded_model.load_state_dict(torch.load(model_path))
        loaded_model.eval()
        self.loaded_model = loaded_model.to(self.device)
        self.Transform = get_transform(train=False)

    def predict(self, image: Image.Image):
        # image: An pil image is expected to be the input

        image, _ = self.Transform(
            image, image
        )  # Transform requires input and target, we dont have target
        with torch.no_grad():
            prediction = self.loaded_model([image.to(self.device)])
        image = Image.fromarray(
            prediction[0]["masks"][0, 0].mul(255).byte().cpu().numpy()
        )
        return image
