#In MVVN, Model View ViewModel architecture, Model represents the data in the application.
#here
from model.fileIOModelMixin import FileIOModelMixin
from model.databaseModelMixin import DatabaseModelMixin 
from model.initialLoadModelMixin import InitialLoadModelMixin
class MainModel(InitialLoadModelMixin, FileIOModelMixin, DatabaseModelMixin):
    def __init__(self):
        pass
