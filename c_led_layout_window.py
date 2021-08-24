import sys

import pyqtgraph
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils

import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class LedLayoutWindow(QWidget):
    def __init__(self, led_wall_w, led_wall_h, margin):
        super(LedLayoutWindow, self).__init__()
        self.setWindowTitle("LED Wall")
        self.resize(led_wall_w*2 + margin*2, led_wall_h*2 + margin*2)
        self.led_wall_w = led_wall_w
        self.led_wall_h = led_wall_h
        self.led_fake_label = QLabel(self)
        self.led_fake_pixmap = utils.qtui_utils.gen_led_layout_pixmap(led_wall_w, led_wall_h, margin, Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label.setPixmap(self.led_fake_pixmap)

        self.gen_single_cabinet_label(40, 24)
        self.led_fake_label.setScaledContents(True)



    #def resize(self, a0: QSize) -> None:
    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.led_fake_label.resize(int(self.width()), int(self.height()))
        a0.accept()

    def wheelEvent(self, a0: QWheelEvent) -> None:
        if a0.angleDelta().y() > 0:
            self.resize(int(self.width()*1.1), int(self.height()*1.1))
        else :
            self.resize(int(self.width() * 0.9), int(self.height() * 0.9))
        self.led_fake_label.resize(int(self.width()), int(self.height()))

        self.single_cabinet_label.resize(int(self.width()*0.2), int(self.height()*0.2))
        log.debug("width : %d", self.width())
        log.debug("height : %d", self.height())
        a0.accept()

    def change_led_wall_res(self, led_wall_w, led_wall_h, margin):
        log.debug("")
        self.resize(led_wall_w * 2 + margin * 2, led_wall_h * 2 + margin * 2)
        self.led_fake_pixmap = utils.qtui_utils.gen_led_layout_pixmap(led_wall_w, led_wall_h, margin, Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label.setPixmap(self.led_fake_pixmap)
        self.led_fake_label.resize(int(self.width()), int(self.height()))

    def gen_single_cabinet_label(self, cabinet_w, cabinet_h):
        self.single_cabinet_pixmap = utils.qtui_utils.gen_led_cabinet_pixmap(cabinet_w, cabinet_h, 0,
                                                                             Qt.GlobalColor.transparent, Qt.GlobalColor.blue, 0x80, 0)
        self.single_cabinet_label = QLabel(self)
        self.single_cabinet_label.setPixmap(self.single_cabinet_pixmap)
        #self.single_cabinet_label.setStyleSheet("background-color : rgba(0,0,0,90%)")
        self.single_cabinet_label.setScaledContents(True)