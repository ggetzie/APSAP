from .load_finds import LoadFinds
from .load_plys import LoadPlys
from .load_3d_model_to_window import Load3dModelToWindowMixin
from .load_1_jpg_pair import Load1jpgPairMixin

class LoadDataMixin(LoadFinds, LoadPlys, Load3dModelToWindowMixin, Load1jpgPairMixin):
    """The function inherits other mixins related to loading data
    """    
    pass
