from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import utils.qtui_utils
from g_defs.c_cabinet_params import cabinet_params
from global_def import *
import utils.log_utils
import qdarkstyle, requests, sys, time, random, json, datetime, re

log = utils.log_utils.logging_init(__file__)

class NewPlaylistDialog(QWidget):
    signal_new_playlist_generate = pyqtSignal(str)
    def __init__(self):
        super(NewPlaylistDialog, self).__init__()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + \
                      """
                      QMenu{
                          button-layout : 2;
                          font: bold 16pt "Brutal Type";
                          border: 3px solid #FFA042;
                          border-radius: 8px;
                          }
                      """)
        self.setWindowTitle("New Playlist")
        self.init_ui()

    def init_ui(self):
        self.setFixedSize(400, 200)
        ''' Total frame layout'''
        self.layout = QGridLayout(self)

        layoutwidget = QFrame()
        layoutgridbox = QGridLayout()
        layoutwidget.setLayout(layoutgridbox)

        self.new_playlist_lable = QLabel()
        self.new_playlist_lable.setText("New Playlist Name")

        self.new_playlist_textedit = QTextEdit()
        self.new_playlist_textedit.setText("New Playlist Name")
        self.new_playlist_textedit.setFixedHeight(40)

        self.confirm_btn = QPushButton()
        self.confirm_btn.setText("OK")
        self.confirm_btn.setFixedWidth(80)
        self.cancel_btn = QPushButton()
        self.cancel_btn.setText("cancle")
        self.cancel_btn.setFixedWidth(80)
        layoutgridbox.addWidget(self.new_playlist_lable, 0, 1)
        layoutgridbox.addWidget(self.new_playlist_textedit, 1, 1)
        layoutgridbox.addWidget(self.cancel_btn, 2, 2)
        layoutgridbox.addWidget(self.confirm_btn, 2, 3)

        self.layout.addWidget(layoutwidget)

        self.confirm_btn.clicked.connect(self.confirm_btn_clicked)
        self.cancel_btn.clicked.connect(self.cancel_btn_clicked)

    def confirm_btn_clicked(self):
        log.debug("")
        self.signal_new_playlist_generate.emit(self.new_playlist_textedit.toPlainText())
        self.destroy()

    def cancel_btn_clicked(self):
        log.debug("")
        self.destroy()