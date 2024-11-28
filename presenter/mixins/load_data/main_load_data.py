from presenter.mixins.load_data.load_3d_model_to_window import Load3dModelToWindowMixin
from presenter.mixins.load_data.load_1_jpg_pair import Load1jpgPairMixin


class LoadDataMixin(Load3dModelToWindowMixin, Load1jpgPairMixin):
    """The function inherits other mixins related to loading data"""
