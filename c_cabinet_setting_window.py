from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils
from g_defs.c_cabinet_params import cabinet_params
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

class CabinetSettingWindow(QWidget):
    def __init__(self,  c_params, **kwargs):
        super(CabinetSettingWindow, self).__init__()
        if c_params is None:
            self.cabinet_params = cabinet_params(0, 0, 0, -1, 0, 0)



        self.setWindowTitle("cabinet setting")
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 400)
        ''' Total frame layout'''
        self.layout = QGridLayout(self)
        self.radio_layout_type_groupbox = QGroupBox("Cabinet Layout Type:", checkable=False)
        self.layout.addWidget(self.radio_layout_type_groupbox)

        self.radio_layout_type_groupbox_gridboxlayout = QGridLayout()
        self.radio_layout_type_groupbox.setLayout(self.radio_layout_type_groupbox_gridboxlayout, )

        self.radio_layout_types = []

        for i in range(8):
            radio_layout_type = QRadioButton()
            test_pixmap = utils.qtui_utils.gen_led_layout_type_pixmap(48, 48, 10, 1)
            icon = QIcon(test_pixmap)
            radio_layout_type.setIcon(icon)
            radio_layout_type.setIconSize(QSize(172, 48))
            self.radio_layout_types.append(radio_layout_type)


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
        self.cabinet_width_textedit = QTextEdit()
        self.cabinet_width_textedit.setFixedSize(45, 30)
        self.cabinet_width_textedit.setText("40 ")

        self.cabinet_height_label = QLabel()
        self.cabinet_height_label.setText("Cabinet Height: ")
        self.cabinet_height_textedit = QTextEdit()
        self.cabinet_height_textedit.setText("24 ")
        self.cabinet_height_textedit.setFixedSize(45, 30)

        ''' Start X'''
        self.cabinet_startx_label = QLabel()
        self.cabinet_startx_label.setText("Cabinet StartX: ")
        self.cabinet_startx_textedit = QTextEdit()
        self.cabinet_startx_textedit.setText("24 ")
        self.cabinet_startx_textedit.setFixedSize(45, 30)

        ''' Start Y'''
        self.cabinet_starty_label = QLabel()
        self.cabinet_starty_label.setText("Cabinet StartY: ")
        self.cabinet_starty_textedit = QTextEdit()
        self.cabinet_starty_textedit.setText("24 ")
        self.cabinet_starty_textedit.setFixedSize(45, 30)

        self.confirm_btn = QPushButton()
        self.confirm_btn.setText("OK")
        self.concel_btn = QPushButton()
        self.concel_btn.setText("Cancel")

        testgridbox.addWidget(self.cabinet_width_label, 0, 0)
        testgridbox.addWidget(self.cabinet_width_textedit, 0, 1)
        testgridbox.addWidget(self.cabinet_height_label, 1, 0)
        testgridbox.addWidget(self.cabinet_height_textedit, 1, 1)

        testgridbox.addWidget(self.cabinet_startx_label, 2, 0)
        testgridbox.addWidget(self.cabinet_startx_textedit, 2, 1)
        testgridbox.addWidget(self.cabinet_starty_label, 3, 0)
        testgridbox.addWidget(self.cabinet_starty_textedit, 3, 1)

        testgridbox.addWidget(self.confirm_btn, 3, 3)
        testgridbox.addWidget(self.concel_btn, 3, 2)


        self.layout.addWidget(testwidget, 1, 0)


        self.layout.setColumnStretch(0, 5)
        self.layout.setRowStretch(0, 5)



        self.show()

