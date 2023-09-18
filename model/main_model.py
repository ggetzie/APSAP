# In MVVN, Model View ViewModel architecture, Model represents the data in the application.

# here

from model.mixins.file_IO import FileIOMixin

from model.mixins.database import DatabaseMixin

from model.mixins.initial_load import InitialLoadMixin

from model.mixins.copy_file import CopyFileMixin


class MainModel(InitialLoadMixin, FileIOMixin, DatabaseMixin, CopyFileMixin):
    pass
    
     

