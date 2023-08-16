from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils
from g_defs.c_cabinet_params import cabinet_params
from global_def import *




class CabinetSettingWindow(QWidget):
    signal_set_cabinet_params = pyqtSignal(cabinet_params)
    signal_draw_temp_cabinet = pyqtSignal(cabinet_params, Qt.GlobalColor)
    signal_set_default_cabinet_resolution = pyqtSignal(int, int)

    def __init__(self,  c_params, **kwargs):
        super(CabinetSettingWindow, self).__init__()
        if c_params is None:
            self.cabinet_params = cabinet_params("?", -1, 0, 0, 0, 0, 0, 0)
            self.cabinet_params_bak = cabinet_params("?", -1, 0, 0, 0, 0, 0, 0)
        self.setWindowTitle("cabinet setting")
        self.init_ui()

        '''signal/slot connect'''
        self.confirm_btn.clicked.connect(self.confirm_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)
        self.set_res_as_default_btn.clicked.connect(self.set_res_as_default_btn_clicked)
        self.cabinet_width_textedit.textChanged.connect(self.cabinet_width_textChanged)
        self.cabinet_height_textedit.textChanged.connect(self.cabinet_height_textChanged)
        self.cabinet_startx_textedit.textChanged.connect(self.cabinet_startx_textChanged)
        self.cabinet_starty_textedit.textChanged.connect(self.cabinet_starty_textChanged)


    def init_ui(self):
        self.setFixedSize(600, 500)
        ''' Total frame layout'''
        self.layout = QGridLayout(self)


        '''set client id & ip label'''
        c_ip_widget = QFrame()
        c_ip_gridbox = QGridLayout()
        c_ip_widget.setLayout(c_ip_gridbox)
        self.client_ip_label = QLabel()
        self.client_ip_label.setText(self.cabinet_params.client_ip)
        self.client_ip_label.setFont(QFont(qfont_style_default, qfont_style_size_extra_large))
        # self.client_ip_label.setFixedSize(200, 30)
        c_ip_gridbox.addWidget(self.client_ip_label, 0, 0)
        self.layout.addWidget(c_ip_widget)

        ''' radio btn group of layout type'''
        self.radio_layout_type_groupbox = QGroupBox("Cabinet Layout Type:", checkable=False)
        self.layout.addWidget(self.radio_layout_type_groupbox, 1, 0)

        self.radio_layout_type_groupbox_gridboxlayout = QGridLayout()
        self.radio_layout_type_groupbox.setLayout(self.radio_layout_type_groupbox_gridboxlayout)

        self.radio_layout_types = []

        for i in range(8):
            radio_layout_type = QRadioButton()
            test_pixmap = utils.qtui_utils.gen_led_layout_type_pixmap(48, 48, 10, i)
            icon = QIcon(test_pixmap)
            radio_layout_type.setIcon(icon)
            radio_layout_type.setIconSize(QSize(172, 48))
            self.radio_layout_types.append(radio_layout_type)
            self.radio_layout_types[i].toggled.connect(self.radio_layout_types_toggled)
        for i in range(8):
            if i < 4:
                self.radio_layout_type_groupbox_gridboxlayout.addWidget(self.radio_layout_types[i], 0, i%4)
            else:
                self.radio_layout_type_groupbox_gridboxlayout.addWidget(self.radio_layout_types[i], 1, i % 4)


        ''' '''
        testwidget = QFrame()
        testgridbox = QGridLayout()
        testwidget.setLayout(testgridbox)
        self.cabinet_width_label = QLabel()
        self.cabinet_width_label.setText("Cabinet Width: ")
        self.cabinet_width_label.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.cabinet_width_textedit = QTextEdit()
        self.cabinet_width_textedit.setFixedSize(90, 40)
        self.cabinet_width_textedit.setText("40 ")
        self.cabinet_width_textedit.setFont(QFont(qfont_style_default, qfont_style_size_large))

        self.cabinet_height_label = QLabel()
        self.cabinet_height_label.setText("Cabinet Height: ")
        self.cabinet_height_label.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.cabinet_height_textedit = QTextEdit()
        self.cabinet_height_textedit.setText("24 ")
        self.cabinet_height_textedit.setFixedSize(90, 40)
        self.cabinet_height_textedit.setFont(QFont(qfont_style_default, qfont_style_size_large))

        ''' Start X'''
        self.cabinet_startx_label = QLabel()
        self.cabinet_startx_label.setText("Cabinet StartX: ")
        self.cabinet_startx_label.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.cabinet_startx_textedit = QTextEdit()
        self.cabinet_startx_textedit.setText("24 ")
        self.cabinet_startx_textedit.setFixedSize(90, 40)
        self.cabinet_startx_textedit.setFont(QFont(qfont_style_default, qfont_style_size_large))

        ''' Start Y'''
        self.cabinet_starty_label = QLabel()
        self.cabinet_starty_label.setText("Cabinet StartY: ")
        self.cabinet_starty_label.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.cabinet_starty_textedit = QTextEdit()
        self.cabinet_starty_textedit.setText("24 ")
        self.cabinet_starty_textedit.setFixedSize(90, 40)
        self.cabinet_starty_textedit.setFont(QFont(qfont_style_default, qfont_style_size_large))

        self.set_res_as_default_btn = QPushButton()
        self.set_res_as_default_btn.setText("set default")
        self.set_res_as_default_btn.adjustSize()
        self.set_res_as_default_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.confirm_btn = QPushButton()
        self.confirm_btn.setText("OK")
        self.confirm_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        self.cancel_btn = QPushButton()
        self.cancel_btn.setText("Cancel")
        self.cancel_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))

        testgridbox.addWidget(self.cabinet_width_label, 0, 0)
        testgridbox.addWidget(self.cabinet_width_textedit, 0, 1)
        testgridbox.addWidget(self.cabinet_height_label, 1, 0)
        testgridbox.addWidget(self.cabinet_height_textedit, 1, 1)

        testgridbox.addWidget(self.cabinet_startx_label, 2, 0)
        testgridbox.addWidget(self.cabinet_startx_textedit, 2, 1)
        testgridbox.addWidget(self.cabinet_starty_label, 3, 0)
        testgridbox.addWidget(self.cabinet_starty_textedit, 3, 1)

        testgridbox.addWidget(self.set_res_as_default_btn, 1, 2)
        testgridbox.addWidget(self.confirm_btn, 3, 3)
        testgridbox.addWidget(self.cancel_btn, 3, 2)


        self.layout.addWidget(testwidget, 2, 0)

        self.layout.setColumnStretch(0, 5)
        self.layout.setRowStretch(0, 5)

        #self.show()

    def set_params(self, c_params):
        self.cabinet_params = c_params
        ''' repoduce a bak '''
        self.cabinet_params_bak = cabinet_params(self.cabinet_params.client_ip, self.cabinet_params.client_id,
                                                 self.cabinet_params.port_id, self.cabinet_params.cabinet_width,
                                                 self.cabinet_params.cabinet_height, self.cabinet_params.layout_type,
                                                 self.cabinet_params.start_x, self.cabinet_params.start_y)
        log.debug('port_id : %d', self.cabinet_params.port_id)
        self.client_ip_label.setText(self.cabinet_params.client_ip
                                     + ", id:" + str(self.cabinet_params.client_id)
                                     + ", port:" + str(self.cabinet_params.port_id))
        self.cabinet_width_textedit.setText(str(self.cabinet_params.cabinet_width))
        self.cabinet_height_textedit.setText(str(self.cabinet_params.cabinet_height))
        self.cabinet_startx_textedit.setText(str(self.cabinet_params.start_x))
        self.cabinet_starty_textedit.setText(str(self.cabinet_params.start_y))
        self.radio_layout_types[c_params.layout_type].setChecked(True)

    def confirm_btn_clicked(self):
        log.debug("")
        self.cabinet_params.cabinet_width = int(self.cabinet_width_textedit.toPlainText())
        self.cabinet_params.cabinet_height = int(self.cabinet_height_textedit.toPlainText())
        self.cabinet_params.start_x = int(self.cabinet_startx_textedit.toPlainText())
        self.cabinet_params.start_y = int(self.cabinet_starty_textedit.toPlainText())
        for i in range(len(self.radio_layout_types)):
            if self.radio_layout_types[i].isChecked():
                log.debug('self.radio_layout_types is %d', i)
                self.cabinet_params.layout_type = i
        self.signal_set_cabinet_params.emit(self.cabinet_params)
        self.signal_draw_temp_cabinet.emit(self.cabinet_params, Qt.GlobalColor.red)
        self.hide()

    def cancel_btn_clicked(self):
        log.debug("")
        self.signal_draw_temp_cabinet.emit(self.cabinet_params, Qt.GlobalColor.red)
        # self.signal_draw_temp_cabinet.emit(self.cabinet_params, Qt.GlobalColor.)
        self.hide()

    def closeEvent(self, event):
        log.debug("")
        self.signal_draw_temp_cabinet.emit(self.cabinet_params, Qt.GlobalColor.red)
        # self.signal_draw_temp_cabinet.emit(self.cabinet_params, None)
        self.hide()

    def set_res_as_default_btn_clicked(self):
        log.debug("")
        self.signal_set_default_cabinet_resolution.emit(int(self.cabinet_width_textedit.toPlainText()),
                                                        int(self.cabinet_height_textedit.toPlainText()))


    def cabinet_width_textChanged(self):
        self.cabinet_params_bak.cabinet_width = int(self.cabinet_width_textedit.toPlainText())
        self.signal_draw_temp_cabinet.emit(self.cabinet_params_bak, Qt.GlobalColor.yellow)

    def cabinet_height_textChanged(self):
        self.cabinet_params_bak.cabinet_height = int(self.cabinet_height_textedit.toPlainText())
        self.signal_draw_temp_cabinet.emit(self.cabinet_params_bak, Qt.GlobalColor.yellow)

    def cabinet_startx_textChanged(self):
        self.cabinet_params_bak.start_x = int(self.cabinet_startx_textedit.toPlainText())
        self.signal_draw_temp_cabinet.emit(self.cabinet_params_bak, Qt.GlobalColor.yellow)

    def cabinet_starty_textChanged(self):
        self.cabinet_params_bak.start_y = int(self.cabinet_starty_textedit.toPlainText())
        self.signal_draw_temp_cabinet.emit(self.cabinet_params_bak, Qt.GlobalColor.yellow)

    def radio_layout_types_toggled(self, is_selected):
        log.debug('')
        if is_selected is False:
            return
        radiobtn = self.sender()

        i = 0
        for radio_layout_type in self.radio_layout_types:
            if radio_layout_type == radiobtn:
                log.debug('radio_layout_type : %d', i)
                self.cabinet_params_bak.layout_type = i
                self.signal_draw_temp_cabinet.emit(self.cabinet_params_bak, Qt.GlobalColor.yellow)
                break
            i += 1

    def __del__(self):
        log.debug("")

