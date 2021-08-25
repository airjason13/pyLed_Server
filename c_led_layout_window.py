import sys

import pyqtgraph
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils

import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class LedLayoutWindow(QWidget):
    def __init__(self, led_wall_w, led_wall_h, cabinet_w, cabinet_h, margin):
        super(LedLayoutWindow, self).__init__()
        self.scale_factor = 4
        self.setWindowTitle("LED Wall")
        self.resize(led_wall_w*self.scale_factor + margin*2, led_wall_h*self.scale_factor + margin*2)
        self.led_wall_w = led_wall_w
        self.led_wall_h = led_wall_h
        self.cabinet_w = cabinet_w
        self.cabinet_h = cabinet_h
        self.led_wall_margin = 10

        '''Gen led wall layout with scalable'''
        self.led_wall_pixel_pixmap = utils.qtui_utils.gen_led_layout_pixmap(self.led_wall_w, self.led_wall_h, self.led_wall_margin,
                                                                           Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label = Droppable_led_label(self.led_wall_pixel_pixmap, self)
        print("led_fake_label label width", self.led_fake_label.width())
        print("led_fake_label label height", self.led_fake_label.height())

        self.single_cabinet_label = self.gen_single_cabinet_label(self.cabinet_w, self.cabinet_h, 0, 0)
        self.led_fake_label.set_drag_label(self.single_cabinet_label)
        print("single_cabinet_label label width", self.single_cabinet_label.width())
        print("single_cabinet_label label height", self.single_cabinet_label.height())

        '''drag_label_ori_offset 為drag_label內之座標, 為QPoint'''
        self.drag_label_ori_offset = None
        self.drag_label_ori_pos = None
        self.drag_label = None
        self.single_cabinet_label.start_drag_signal.connect(self.start_drag)

    def start_drag(self, drag_label, start_offset):
        log.debug('start_drag')
        self.drag_label = drag_label
        self.drag_label_ori_pos = self.drag_label.pos()
        ##self.drag_label.move(start_offset)
        print(self.drag_label_ori_pos)
        self.drag_label_ori_offset = start_offset
        print(start_offset)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.led_fake_label.resize(int(self.width()), int(self.height()))
        a0.accept()

    def wheelEvent(self, a0: QWheelEvent) -> None:
        #scale_factor = 1
        if a0.angleDelta().y() > 0:
            scale_factor = 1.1
        else :
            scale_factor = 0.9
        self.resize(int(self.width() * scale_factor), int(self.height() * scale_factor))
        self.single_cabinet_label.resize(int(self.single_cabinet_label.width() * scale_factor),
                                         int(self.single_cabinet_label.height() * scale_factor))
        self.led_fake_label.resize(int(self.width()), int(self.height()))

        log.debug("width : %d", self.width())
        log.debug("height : %d", self.height())
        a0.accept()

    def change_led_wall_res(self, led_wall_w, led_wall_h, margin):
        log.debug("")
        self.resize(led_wall_w * 2 + margin * 2, led_wall_h * 2 + margin * 2)
        self.led_fake_pixmap = utils.qtui_utils.gen_led_layout_pixmap(led_wall_w, led_wall_h, margin,
                                                                      Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label.setPixmap(self.led_fake_pixmap)
        self.led_fake_label.resize(int(self.width()), int(self.height()))

    def gen_single_cabinet_label(self, cabinet_w, cabinet_h, start_x, start_y):
        self.single_cabinet_pixmap = utils.qtui_utils.gen_led_cabinet_pixmap(cabinet_w, cabinet_h, 0,
                                                                             Qt.GlobalColor.transparent, Qt.GlobalColor.red, 0x80, 0)
        return Draggable_cabinet_label(self, self.single_cabinet_pixmap, start_x, start_y)


class Draggable_cabinet_label(QLabel):
    start_drag_signal = pyqtSignal(QLabel, QPoint)
    def __init__(self, parent, image, start_x, start_y):
        super(QLabel, self).__init__(parent)
        self.setPixmap(QPixmap(image))
        self.setScaledContents(True)
        self.move(start_x, start_y)
        self.show()

    def mousePressEvent(self, event):
        log.debug('mousePressEvent')
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.start_drag_signal.emit(self, self.drag_start_position)


    def mouseMoveEvent(self, event):
        log.debug('mouseMoveEvent')
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(self.text())
        mimedata.setImageData(self.pixmap().toImage())

        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.size())
        painter = QPainter(pixmap)
        painter.drawPixmap(self.rect(), self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction | Qt.MoveAction)

class Droppable_led_label(QLabel):
    def __init__(self, image, parent):
        super().__init__( parent)

        self.setPixmap(QPixmap(image))
        self.setScaledContents(True)
        self.setAcceptDrops(True)




    def dragEnterEvent(self, event):
        log.debug("dragEnterEvent")
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def set_drag_label(self, drag_label):
        self.drag_label = drag_label

    def dropEvent(self, event):
        log.debug("dropEvent")
        pos = event.pos()
        #改成用pyqtsignal處理可能比較好
        self.drag_label.move(pos)
        event.acceptProposedAction()