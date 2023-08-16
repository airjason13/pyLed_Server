from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTreeWidget, QTableWidget, QWidget, QVBoxLayout, QTableWidgetItem
from global_def import *



class clients_page(QObject):
    def __init__(self, mainwindow, clients, **kwargs):
        super(clients_page, self).__init__(**kwargs)
        self.clients = clients
        self.mainwindow = mainwindow
        self.client_table = QTableWidget(self.mainwindow.right_frame)
        self.client_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        ''' ip, id, status, version'''
        self.client_table.setColumnCount(4)
        self.client_table.setRowCount(0)
        self.client_table.setMouseTracking(True)
        self.client_table.horizontalHeader().setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.client_table.setHorizontalHeaderLabels(['IP', 'ID', 'STATUS', 'VERSION'])
        self.client_table.setColumnWidth(0, 200)  # IP Column width:200
        self.client_table.setColumnWidth(2, 200)  # Version Column width:200
        self.client_table.setColumnWidth(3, 200)  # Version Column width:200
        client_widget = QWidget(self.mainwindow.right_frame)
        client_layout = QVBoxLayout()
        client_widget.setLayout(client_layout)
        client_layout.addWidget(self.client_table)
        # right click menu
        self.client_table.setContextMenuPolicy(Qt.CustomContextMenu)
        # connect the signal/slot
        self.client_table.customContextMenuRequested.connect(self.mainwindow.clientsmenucontexttree)
        self.mainwindow.right_layout.addWidget(client_widget)

    '''refresh the array only'''
    def refresh_clients(self, clients):
        self.clients = clients

    '''refresh the array only'''
    def refresh_client_table(self):
        row_count = self.client_table.rowCount()
        for i in range(row_count):
            row_to_remove = self.client_table.rowAt(i)
            self.client_table.removeRow(row_to_remove)

        for c in self.clients:
            row_count = self.client_table.rowCount()
            self.client_table.insertRow(row_count)
            self.client_table.setItem(row_count, 0, QTableWidgetItem(c.client_ip))
            self.client_table.setItem(row_count, 1, QTableWidgetItem(str(c.client_id)))
            self.client_table.setItem(row_count, 3, QTableWidgetItem(c.client_version))