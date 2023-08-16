from PyQt5.QtCore import QObject
from global_def import *

class mediafileparam(QObject):
    def __init__(self, file_uri, **kwargs):
        super(mediafileparam, self).__init__(**kwargs)
        self.file_uri = file_uri
        self.thumbnail_uri = "test"
