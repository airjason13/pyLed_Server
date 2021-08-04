from asyncore import loop

from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt5 import QtWidgets, QtGui, QtCore, QtNetwork
import time
import utils.log_utils

log = utils.log_utils.logging_init()

class Worker(QThread):
    def __init__(self, parent=None, method=None, **kwargs):
        super(Worker, self).__init__(parent)
        self.method = method
        #print("kwargs:", kwargs)
        self.kwargs = kwargs
        # self.count = 0
        #self.loop = loop(method= self.method)

    def run(self):
        while True:
            time.sleep(0.1)

            self.method(self.kwargs)



class loop(object):

    def __init__(self, method=None):
        self.count = 0
        self.method = method

    def methodA(self):
        while True:
            time.sleep(3)
            self.method()
