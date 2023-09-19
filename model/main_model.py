# In MVVN, Model View ViewModel architecture, Model represents the data in the application.

from model.mixins.file_IO import FileIOMixin
from model.mixins.database import DatabaseMixin
from model.mixins.initial_load import InitialLoadMixin
from model.mixins.copy_file import CopyFileMixin


class MainModel(InitialLoadMixin, FileIOMixin, DatabaseMixin, CopyFileMixin):
    """The MainModel contains data-related libraries and functions, imported from various mixins.

    Args:
        InitialLoadMixin (class): This mixin contains the function prepare_data() along with other functions to help with the initial loading of the whole application
        FileIOMixin (class): This mixin contains the functions related to opening JSON and Image files
        DatabaseMixin (class): This mixin contains the functions related to get and upate the ceremic find information from the database
        CopyFileMixin (class): This mixin contains the function fixAndCopyPly() that opens a 3d model, fixes it, then save it to another place.
    """    
    pass
    
     

