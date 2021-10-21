from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDesktopWidget, QStyleFactory, QWidget, QHBoxLayout, QVBoxLayout, QFormLayout,
                            QGridLayout, QFrame,QHeaderView, QTableWidgetItem, QMessageBox, QFileDialog,
                            QSlider, QLabel, QLineEdit, QPushButton, QTableWidget, QStackedLayout, QSplitter, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator,
                             QFileDialog, QListWidget, QFileSystemModel, QTreeView, QMenu, QAction, QAbstractItemView, QItemDelegate)
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont, QMovie, QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt, QMutex, pyqtSlot, QModelIndex, pyqtSignal, QSize
import pyqtgraph as pg
import qdarkstyle, requests, sys, time, random, json, datetime, re
from PyQt5.QtCore import QObject
import utils.log_utils



log = utils.log_utils.logging_init(__file__)

def set_qstyle_dark(QObject):
    try:
        QObject.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + \
                              """
                              QMenu{
                                  button-layout : 2;
                                  font: bold 16pt "Brutal Type";
                                  border: 3px solid #FFA042;
                                  border-radius: 8px;
                                  }
                              """)
    except Exception as e:
        log.error(e)

