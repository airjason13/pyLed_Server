from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTreeWidget, QApplication, QLabel, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class CTreeWidget(QTreeWidget):
    mouseMove = pyqtSignal(QMouseEvent)
    def mouseMoveEvent(self, event):
        #log.debug("%d, %d", event.x(), event.y())
        #log.debug("%s", self.itemAt(event.x(), event.y()).text(0))
        self.mouseMove.emit(event)

        """if QApplication.keyboardModifiers()&(Qt.ShiftModifier|Qt.ControlModifier):
            log.debug("mouseMoveEvent")
            QTreeWidget.mouseMoveEvent(self, event)"""

    """def mousePressEvent(self, event):
        if QApplication.keyboardModifiers()&(Qt.ShiftModifier|Qt.ControlModifier):
            log.debug("mousePressEvent")
            QTreeWidget.mousePressEvent(self, event)"""
