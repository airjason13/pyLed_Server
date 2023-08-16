from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils
from global_def import *


class LedLayoutWindow(QWidget):
    def __init__(self, led_wall_w, led_wall_h, cabinet_w, cabinet_h, margin):
        super(LedLayoutWindow, self).__init__()
        self.scale_factor = 8 #need to set into drag and drop label
        self.led_wall_margin = margin
        self.setStyleSheet("background-color: black;")
        self.setWindowTitle("LED Wall layout")

        self.led_wall_w = led_wall_w
        self.led_wall_h = led_wall_h
        self.cabinet_w = cabinet_w
        self.cabinet_h = cabinet_h
        self.led_pinch = 8
        '''Gen led wall layout with scalable'''
        self.led_wall_pixel_pixmap = utils.qtui_utils.gen_led_layout_pixmap(self.led_wall_w, self.led_wall_h,
                                                                            self.led_wall_margin,
                                                                           Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label = Droppable_led_label(self.led_wall_pixel_pixmap, self)

        self.single_cabinet_labels = []
        self.cabinet_pixmaps = []

        '''drag_label_ori_offset 為drag_label內之座標, 為QPoint'''
        self.drag_label_ori_offset = None
        self.drag_label_ori_pos = None
        self.drag_label = None
        self.led_fake_label.label_drop_signal.connect(self.label_drop)

        self.setFixedWidth(led_wall_w * self.scale_factor + margin * 2)
        self.setFixedHeight(led_wall_h * self.scale_factor + margin * 2)
        self.led_fake_label.move(0, 0)

    ''' slot function for start drag'''
    def start_drag(self, drag_label, start_offset):
        log.debug('start_drag')
        log.debug("%s", drag_label)
        if self.drag_label is not None:
            return
        self.drag_label = drag_label
        self.drag_label_ori_pos = self.drag_label.pos()

        log.debug(self.drag_label_ori_pos)
        self.drag_label_ori_offset = start_offset
        log.debug(start_offset)

    ''' slot function for drop signal'''
    def label_drop_on_drag_label(self, drop_label, pos):
        log.fatal('label_drop_on_drag_label')
        # log.fatal('Do not do this')
        # return
        log.debug("%s",  drop_label)
        log.debug("pos.x() : %d", pos.x())
        log.debug("pos.y() : %d", pos.y())
        log.debug("self.drag_label_ori_pos.x() : %d", self.drag_label_ori_pos.x())
        log.debug("self.drag_label_ori_pos.y() : %d", self.drag_label_ori_pos.y())

        drop_global_x = pos.x() + drop_label.x()
        drop_global_y = pos.y() + drop_label.y()
        final_pos_x_tmp = drop_global_x - self.drag_label_ori_offset.x() + self.drag_label_ori_pos.x()
        final_pos_y_tmp = drop_global_y - self.drag_label_ori_offset.y() + self.drag_label_ori_pos.y()
        final_pos_x = final_pos_x_tmp
        final_pos_y = final_pos_y_tmp
        log.debug("final_pos_x_tmp : %d", final_pos_x_tmp)
        log.debug("final_pos_y_tmp : %d", final_pos_y_tmp)
        '''re-match'''
        '''x_pix_factor 為 對應的led_wall 的 x點數座標'''
        '''y_pix_factor 為 對應的led_wall 的 y點數座標'''
        x_pix_factor = int(final_pos_x/self.scale_factor)
        y_pix_factor = int(final_pos_y / self.scale_factor)
        if (final_pos_x_tmp - self.led_wall_margin ) % (self.scale_factor ) > (self.scale_factor/2):
            x_pix_factor = int((final_pos_x_tmp - self.led_wall_margin ) / (self.scale_factor ))
            final_pos_x = self.led_wall_margin + x_pix_factor*self.scale_factor
        else:
            x_pix_factor = int((final_pos_x_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_x = self.led_wall_margin + x_pix_factor * self.scale_factor

        if (final_pos_y_tmp - self.led_wall_margin ) % (self.scale_factor ) > (self.scale_factor/2):
            y_pix_factor = int((final_pos_y_tmp - self.led_wall_margin ) / (self.scale_factor ))
            final_pos_y = self.led_wall_margin + y_pix_factor*self.scale_factor
        else:
            y_pix_factor = int((final_pos_y_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_y = self.led_wall_margin + y_pix_factor * self.scale_factor
        log.debug("final_pos_x : %d", final_pos_x)
        log.debug("final_pos_y : %d", final_pos_y)
        log.debug("x_pix_factor : %d", x_pix_factor)
        log.debug("y_pix_factor : %d", y_pix_factor)
        x_compensation, y_compensation = self.get_coordinate_compensation(drop_label.c_params)
        # drop_label.move(final_pos_x + x_compensation, final_pos_y + y_compensation)
        self.drag_label.move(final_pos_x + x_compensation, final_pos_y + y_compensation)

        self.drag_label = None

    ''' slot function for drop signal'''
    def label_drop(self, pos):
        log.debug("label_drop")
        final_pos_x_tmp = (pos.x() - self.drag_label_ori_offset.x()) + self.drag_label_ori_pos.x()
        final_pos_y_tmp = (pos.y() - self.drag_label_ori_offset.y()) + self.drag_label_ori_pos.y()
        final_pos_x = final_pos_x_tmp
        final_pos_y = final_pos_y_tmp
        log.debug("final_pos_x_tmp : %d", final_pos_x_tmp)
        log.debug("final_pos_y_tmp : %d", final_pos_y_tmp)
        '''re-match'''
        '''x_pix_factor 為 對應的led_wall 的 x點數座標'''
        '''y_pix_factor 為 對應的led_wall 的 y點數座標'''
        x_pix_factor = int(final_pos_x / self.scale_factor)
        y_pix_factor = int(final_pos_y / self.scale_factor)
        if (final_pos_x_tmp - self.led_wall_margin) % (self.scale_factor) > (self.scale_factor / 2):
            x_pix_factor = int((final_pos_x_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_x = self.led_wall_margin + x_pix_factor * self.scale_factor
        else:
            x_pix_factor = int((final_pos_x_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_x = self.led_wall_margin + x_pix_factor * self.scale_factor

        if (final_pos_y_tmp - self.led_wall_margin) % (self.scale_factor) > (self.scale_factor / 2):
            y_pix_factor = int((final_pos_y_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_y = self.led_wall_margin + y_pix_factor * self.scale_factor
        else:
            y_pix_factor = int((final_pos_y_tmp - self.led_wall_margin) / (self.scale_factor))
            final_pos_y = self.led_wall_margin + y_pix_factor * self.scale_factor

        log.debug("final_pos_x : %d", final_pos_x)
        log.debug("final_pos_y : %d", final_pos_y)
        log.debug("x_pix_factor : %d", x_pix_factor)
        log.debug("y_pix_factor : %d", y_pix_factor)

        x_compensation, y_compensation = self.get_coordinate_compensation(self.drag_label.c_params)
        self.drag_label.move(final_pos_x + x_compensation, final_pos_y + y_compensation)

        log.debug("port_id: %d", self.drag_label.get_port_id())
        log.debug("layout_type: %d", self.drag_label.get_layout_type())
        self.drag_label = None


    def resizeEvent(self, a0: QResizeEvent) -> None:
        log.debug("resizeEvent")
        log.debug("self.led_fake_label.width() :%d ", self.led_fake_label.width())
        log.debug("self.led_fake_label.height() : %d ", self.led_fake_label.height())
        log.debug("self.width() :%d ", self.width())
        log.debug("self.height() : %d ", self.height())
        # self.led_wall_pixel_pixmap.scaled(self.width(), self.height())
        # self.led_fake_label.setPixmap(self.led_wall_pixel_pixmap)

        a0.accept()

    def wheelEvent(self, a0: QWheelEvent) -> None:
        #scale_factor = 1
        if a0.angleDelta().y() > 0:
            scale_factor = 2
        else:
            scale_factor = 0.5
        log.debug("%s:", self.geometry())
        # self.resize(int(self.width() * scale_factor), int(self.height() * scale_factor))
        self.setFixedWidth(int(self.width() * scale_factor))
        self.setFixedHeight(int(self.height() * scale_factor))
        log.debug("%s:", self.geometry())
        for i in range(len(self.single_cabinet_labels)):
            start_x = self.single_cabinet_labels[i].x() * scale_factor
            start_y = self.single_cabinet_labels[i].y() * scale_factor
            width = self.single_cabinet_labels[i].width() * scale_factor
            height = self.single_cabinet_labels[i].height() * scale_factor
            self.single_cabinet_labels[i].setGeometry(start_x, start_y, width, height)

        self.led_fake_label.resize(int(self.led_fake_label.width() * scale_factor),
                                   int(self.led_fake_label.height() * scale_factor))

        a0.accept()

    def change_led_wall_res(self, led_wall_w, led_wall_h, margin):
        log.debug("")
        # self.resize(led_wall_w * self.scale_factor + margin * 2, led_wall_h * self.scale_factor + margin * 2)
        self.setFixedWidth(led_wall_w * self.scale_factor + margin * 2)
        self.setFixedHeight(led_wall_h * self.scale_factor + margin * 2)
        self.led_fake_pixmap = utils.qtui_utils.gen_led_layout_pixmap(led_wall_w, led_wall_h, margin,
                                                                      Qt.GlobalColor.black, Qt.GlobalColor.white)
        self.led_fake_label.setPixmap(self.led_fake_pixmap)
        self.led_fake_label.resize(int(self.width()), int(self.height()))

    def gen_single_cabinet_label(self, c_params, start_drag_slot, label_drop_slot):
        single_cabinet_label = Draggable_cabinet_label(self, c_params, self.led_pinch, start_drag_slot, label_drop_slot)
        return single_cabinet_label

    def gen_single_cabinet_label_deprecated(self, c_params, start_drag_slot, label_drop_slot):
        self.single_cabinet_pixmap = utils.qtui_utils.gen_led_cabinet_pixmap(c_params.client_ip, c_params.client_id, c_params.port_id,
                                                                             c_params.cabinet_width, c_params.cabinet_height, 0, 1, layout_type=0,
                                                                             bg_color=Qt.GlobalColor.transparent, line_color=Qt.GlobalColor.red,
                                                                             str_color=Qt.GlobalColor.yellow)
        return Draggable_cabinet_label(self, c_params.client_ip, c_params.client_id, c_params.port_id, self.single_cabinet_pixmap,
                                       c_params.start_x, c_params.start_y, self.led_pinch, start_drag_slot, label_drop_slot)


    def add_cabinet_label(self, c_params):
        # log.debug("")
        # log.debug("len(self.single_cabinet_labels) = %d", len(self.single_cabinet_labels))
        tmp_label = self.gen_single_cabinet_label(c_params, self.start_drag, self.label_drop_on_drag_label)
        tmp_cabinet_pixmap = utils.qtui_utils.gen_led_cabinet_pixmap_with_cabinet_params(tmp_label.c_params, margin=0,
                                                                                                bg_color=Qt.GlobalColor.transparent,
                                                                                                line_color=Qt.GlobalColor.red,
                                                                                                str_color=Qt.GlobalColor.yellow)

        tmp_label.setPixmap(QPixmap(tmp_cabinet_pixmap))
        tmp_label.resize(QPixmap(tmp_cabinet_pixmap).width(), QPixmap(tmp_cabinet_pixmap).height())
        tmp_label.setScaledContents(True)
        x_compensation, y_compensation = self.get_coordinate_compensation(c_params)
        label_start_x, label_start_y = self.get_label_start_pos_with_layout_type(c_params)
        tmp_label.move(
            (label_start_x * c_params.led_pinch) + default_led_wall_margin + x_compensation,
            (label_start_y * c_params.led_pinch) + default_led_wall_margin + y_compensation)

        self.single_cabinet_labels.append(tmp_label)
        # log.debug("len(self.single_cabinet_labels) = %d", len(self.single_cabinet_labels))
        tmp_label.show()

    def remove_all_cabinet_label(self):
        log.debug("")
        for i in range(len(self.single_cabinet_labels)):
            self.single_cabinet_labels[i].deleteLater()

        self.single_cabinet_labels.clear()

    ''' 依照 c_params 選定label來更新'''
    def redraw_cabinet_label(self, c_params, line_color):
        log.debug('len of self.single_cabinet_labels :%d', len(self.single_cabinet_labels))
        if line_color is None:
            log.debug("Do not draw this")
            return
        for cabinet_label in self.single_cabinet_labels:
            if cabinet_label.c_params.client_ip is c_params.client_ip:
                if cabinet_label.c_params.port_id == c_params.port_id:
                    log.debug('client ip & port id match')
                    image = utils.qtui_utils.gen_led_cabinet_pixmap_with_cabinet_params(c_params, margin=0,
                                                                    bg_color=Qt.GlobalColor.transparent,
                                                                    line_color=line_color,
                                                                    str_color=Qt.GlobalColor.yellow)
                    cabinet_label.setPixmap(QPixmap(image))
                    cabinet_label.resize(QPixmap(image).width(), QPixmap(image).height())

                    label_start_x, label_start_y = self.get_label_start_pos_with_layout_type(c_params)

                    x_compensation, y_compensation = self.get_coordinate_compensation(c_params)

                    log.debug("label_start_x = %d", label_start_x)
                    log.debug("label_start_y = %d", label_start_y)
                    log.debug("x_compensation = %d", x_compensation)
                    log.debug("y_compensation = %d", y_compensation)
                    cabinet_label.move(
                        (label_start_x * c_params.led_pinch) + default_led_wall_margin + x_compensation,
                        (label_start_y * c_params.led_pinch) + default_led_wall_margin + y_compensation)

                    cabinet_label.show()
                    break

    def get_label_start_pos_with_layout_type(self, c_params):
        x = c_params.start_x
        y = c_params.start_y
        if c_params.layout_type == 0:
            x = c_params.start_x
            y = c_params.start_y
        if c_params.layout_type == 1:
            x = c_params.start_x
            y = c_params.start_y - c_params.cabinet_height + 1
        elif c_params.layout_type == 2:
            x = c_params.start_x - c_params.cabinet_width + 1
            y = c_params.start_y
        elif c_params.layout_type == 3:
            x = c_params.start_x - c_params.cabinet_width + 1
            y = c_params.start_y - c_params.cabinet_height + 1
        elif c_params.layout_type == 4:
            x = c_params.start_x - c_params.cabinet_width + 1
            y = c_params.start_y
        elif c_params.layout_type == 5:
            x = c_params.start_x
            y = c_params.start_y - c_params.cabinet_height + 1
        elif c_params.layout_type == 6:
            x = c_params.start_x - c_params.cabinet_width + 1
            y = c_params.start_y - c_params.cabinet_height + 1
        elif c_params.layout_type == 7:
            x = c_params.start_x
            y = c_params.start_y
        return x, y


    ''' for line interval compensation'''
    def get_coordinate_compensation(self, c_params):
        x = 0
        y = 0

        if c_params.layout_type > 3:
            x = -4
            #y = -4
        else :
            y = -4
        return x, y

class Draggable_cabinet_label(QLabel):
    start_drag_signal = pyqtSignal(QLabel, QPoint)
    label_drop_signal = pyqtSignal(QLabel, QPoint)
    def __init__(self, parent, c_params, led_pinch, start_drag_slot, label_drop_slot):
        super(QLabel, self).__init__(parent)
        self.c_params = c_params
        self.setScaledContents(True)
        self.setAcceptDrops(True)

        self.start_drag_signal.connect(start_drag_slot)
        self.label_drop_signal.connect(label_drop_slot)
        #self.show()


    def set_c_params(self, c_params):
        log.debug('')
        self.c_params = c_params


    def dragEnterEvent(self, event):
        log.debug('dragEnterEvent')

        if event.mimeData().hasImage():
            event.acceptProposedAction()


    def dropEvent(self, event):
        log.debug("dropEvent")
        pos = event.pos()
        self.label_drop_signal.emit(self, pos)



    def mouseReleaseEvent(self, QMouseEvent):
        log.debug('mousePressEvent')

    def mousePressEvent(self, event):
        log.debug('mousePressEvent')
        log.debug('label x : %d', self.x())
        log.debug('label y : %d', self.y())
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos() + self.pos()
            self.start_drag_signal.emit(self, self.drag_start_position)


    def mouseMoveEvent(self, event):

        log.debug(event.pos())
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

    def get_port_id(self):
        log.debug("self.c_params.port_id = %d", self.c_params.port_id)
        return self.c_params.port_id

    def get_layout_type(self):
        log.debug("self.c_params.layout_type = %d", self.c_params.layout_type)
        return self.c_params.layout_type

class Droppable_led_label(QLabel):
    label_drop_signal = pyqtSignal( QPoint)
    def __init__(self, image, parent):
        super().__init__( parent)

        self.setPixmap(QPixmap(image))
        self.resize(QPixmap(image).width(), QPixmap(image).height())

        self.setScaledContents(True)
        self.setAcceptDrops(True)


    def dragEnterEvent(self, event):
        log.debug("dragEnterEvent")
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    #def set_drag_label(self, drag_label):
    #    self.drag_label = drag_label

    def dropEvent(self, event):
        log.debug("dropEvent")
        pos = event.pos()
        self.label_drop_signal.emit(pos)
        event.acceptProposedAction()

class cabinet_pixmap(QObject):
    def __init__(self, c_params, **kwargs):
        self.c_params = c_params
        self.qpixmap_image = utils.qtui_utils.gen_led_cabinet_pixmap_with_cabinet_params(self.c_params, margin=0,
                                                                                                bg_color=Qt.GlobalColor.transparent,
                                                                                                line_color=Qt.GlobalColor.red,
                                                                                                str_color=Qt.GlobalColor.yellow)
