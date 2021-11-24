from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QPalette, QColor, QBrush, QFont
from PyQt5.QtWidgets import QTreeWidget, QTableWidget, QWidget, QVBoxLayout, QTableWidgetItem, QAbstractItemView, \
                            QTreeWidgetItem, QPushButton, QHBoxLayout, QMenu, QAction
from g_defs.c_TreeWidgetItemSP import CTreeWidget
import os
from global_def import *
from set_qstyle import *
from c_new_playlist_dialog import NewPlaylistDialog
from commands_def import *
import utils.log_utils
log = utils.log_utils.logging_init(__file__)

class media_page(QObject):
    def __init__(self, mainwindow, **kwargs):
        super(media_page, self).__init__(**kwargs)
        self.mainwindow = mainwindow
        self.media_engine = mainwindow.media_engine
        self.play_option_repeat = self.mainwindow.play_option_repeat
        self.file_tree = CTreeWidget(self.mainwindow.right_frame)

        self.file_tree.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_tree.setColumnCount(1)
        self.file_tree.setColumnWidth(0, 300)
        self.file_tree.headerItem().setText(0, "Media Files")
        font = QFont()
        font.setPointSize(24)
        self.file_tree.setFont(font)
        # Add Internal Media Folder in tree root

        self.NewPlaylistDialog = None

        self.internal_media_root = QTreeWidgetItem(self.file_tree)

        self.internal_media_root.setText(0, "Internal Media")
        for f in self.mainwindow.media_engine.internal_medialist.filelist:
            internal_file_item = QTreeWidgetItem()
            internal_file_item.setText(0, os.path.basename(f))
            #utils.ffmpy_utils.gen_webp_from_video(internal_media_folder, os.path.basename(f))  # need to remove later
            utils.ffmpy_utils.gen_webp_from_video_threading(internal_media_folder, os.path.basename(f))
            self.internal_media_root.addChild(internal_file_item)

        self.file_tree.addTopLevelItem(self.internal_media_root)

        # Add External Media Folder in tree root
        self.external_media_root = QTreeWidgetItem(self.file_tree)
        self.external_media_root.setText(0, "External Media")  # + ":" + external_media_list.folder_uri)
        child_count = 0
        for external_media_list in self.mainwindow.media_engine.external_medialist:
            external_folder = QTreeWidgetItem()
            external_folder.setText(0, os.path.basename(external_media_list.folder_uri))
            self.external_media_root.addChild(external_folder)
            for f in external_media_list.filelist:
                external_file_item = QTreeWidgetItem()
                external_file_item.setText(0, os.path.basename(f))
                #utils.ffmpy_utils.gen_webp_from_video(external_media_list.folder_uri,
                #                                      os.path.basename(f))  # need to remove later
                utils.ffmpy_utils.gen_webp_from_video_threading(external_media_list.folder_uri, os.path.basename(f))
                self.external_media_root.child(child_count).addChild(external_file_item)
            child_count += 1
            # self.external_media_root_list.append(external_media_root)
        self.file_tree.addTopLevelItem(self.external_media_root)

        # playlist file tree
        self.qtw_media_play_list = QTreeWidgetItem(self.file_tree)
        self.qtw_media_play_list.setText(0, "Playlist")
        for playlist in self.mainwindow.media_engine.playlist:
            playlist_root = QTreeWidgetItem(self.qtw_media_play_list)
            playlist_root.setText(0, playlist.name)
            for file_name in playlist.fileslist:
                log.debug("playlist.fileslist :%s", file_name)
                file_name_item = QTreeWidgetItem(playlist_root)
                file_name_item.setText(0, os.path.basename(file_name))
                playlist_root.addChild(file_name_item)

        self.file_tree.addTopLevelItem(self.qtw_media_play_list)
        self.file_tree.expandAll()

        self.file_tree.setMouseTracking(True)
        # Add right clicked function signal/slot
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.menu_context_tree)

        log.debug("mount point : %s", utils.file_utils.get_mount_points())

        self.play_option_init()
        self.video_params_option_init()

        self.file_tree_widget = QWidget(self.mainwindow.right_frame)
        file_tree_layout = QVBoxLayout()
        self.file_tree_widget.setLayout(file_tree_layout)
        file_tree_layout.addWidget(self.file_tree)
        file_tree_layout.addWidget(self.play_option_widget)
        file_tree_layout.addWidget(self.video_params_widget)
        self.file_tree_widget.setMouseTracking(True)
        self.file_tree.mouseMove.connect(self.mainwindow.media_page_mouseMove)
        self.mainwindow.right_layout.addWidget(self.file_tree_widget)

    def refresh_internal_medialist(self):
        for i in reversed(range(self.internal_media_root.childCount())):
            log.debug("self.medialist_page.internal_media_root.child() = %s",
                      self.internal_media_root.child(i).text(0))
            self.internal_media_root.removeChild(self.internal_media_root.child(i))

        self.internal_media_root.setText(0, "Internal Media")
        for f in self.mainwindow.media_engine.internal_medialist.filelist:
            internal_file_item = QTreeWidgetItem()
            internal_file_item.setText(0, os.path.basename(f))
            # utils.ffmpy_utils.gen_webp_from_video(internal_media_folder, os.path.basename(f))  # need to remove later
            utils.ffmpy_utils.gen_webp_from_video_threading(internal_media_folder, os.path.basename(f))
            self.internal_media_root.addChild(internal_file_item)

    def play_option_init(self):
        """play singal file btn"""
        self.btn_play_select_file = QPushButton(self.mainwindow.right_frame)
        self.btn_play_select_file.setText("Play Select File")
        self.btn_play_select_file.setFixedWidth(media_btn_width)
        self.btn_play_select_file.setDisabled(True)

        """play playlist btn"""
        self.btn_play_playlist = QPushButton(self.mainwindow.right_frame)
        self.btn_play_playlist.setText("Play Playlist")
        self.btn_play_playlist.setFixedWidth(media_btn_width)
        # if len(self.media_play_list) == 0:
        #    self.btn_play_playlist.setDisabled(True)
        self.btn_play_playlist.clicked.connect(self.mainwindow.play_playlist_trigger)

        """stop btn"""
        self.btn_stop = QPushButton(self.mainwindow.right_frame)
        self.btn_stop.setText("Stop")
        self.btn_stop.setFixedWidth(media_btn_width)
        self.btn_stop.clicked.connect(self.stop_media_trigger)
        self.btn_stop.clicked.connect(self.mainwindow.stop_media_set)

        self.btn_pause = QPushButton(self.mainwindow.right_frame)
        self.btn_pause.setText("Pause")
        self.btn_pause.setFixedWidth(media_btn_width)
        self.btn_pause.clicked.connect(self.pause_media_trigger)

        self.btn_repeat = QPushButton(self.mainwindow.right_frame)
        if self.mainwindow.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.mainwindow.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.mainwindow.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")

        self.btn_repeat.setFixedWidth(media_btn_width)
        self.btn_repeat.clicked.connect(self.repeat_option_trigger)

        self.play_option_widget = QWidget(self.mainwindow.right_frame)
        play_option_layout = QHBoxLayout()
        self.play_option_widget.setLayout(play_option_layout)
        play_option_layout.addWidget(self.btn_play_select_file)
        play_option_layout.addWidget(self.btn_play_playlist)
        play_option_layout.addWidget(self.btn_stop)
        play_option_layout.addWidget(self.btn_pause)
        play_option_layout.addWidget(self.btn_repeat)

    def video_params_option_init(self):
        # brightness
        self.brightness_label = QLabel(self.mainwindow.right_frame)
        self.brightness_label.setText("Brightness:")
        self.brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.brightness_edit.setFixedWidth(100)
        self.brightness_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_brightness))

        # contrast
        self.contrast_label = QLabel(self.mainwindow.right_frame)
        self.contrast_label.setText("Contrast:")
        self.contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.contrast_edit.setFixedWidth(100)
        self.contrast_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_contrast))

        # red gain
        self.redgain_label = QLabel(self.mainwindow.right_frame)
        self.redgain_label.setText("Red Gain:")
        self.redgain_edit = QLineEdit(self.mainwindow.right_frame)
        self.redgain_edit.setFixedWidth(100)
        self.redgain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_red_bias))

        # green gain
        self.greengain_label = QLabel(self.mainwindow.right_frame)
        self.greengain_label.setText("Green Gain:")
        self.greengain_edit = QLineEdit(self.mainwindow.right_frame)
        self.greengain_edit.setFixedWidth(100)
        self.greengain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_green_bias))

        # blue gain
        self.blugain_label = QLabel(self.mainwindow.right_frame)
        self.blugain_label.setText("Blue Gain:")
        self.bluegain_edit = QLineEdit(self.mainwindow.right_frame)
        self.bluegain_edit.setFixedWidth(100)
        self.bluegain_edit.setText(str(self.mainwindow.media_engine.media_processor.video_params.video_blue_bias))

        #client brightness adjust
        self.client_brightness_label = QLabel(self.mainwindow.right_frame)
        self.client_brightness_label.setText("Client Br:")
        self.client_brightness_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_brightness_edit.setFixedWidth(100)
        self.client_brightness_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_brightness))

        # client brightness adjust
        self.client_br_divisor_label = QLabel(self.mainwindow.right_frame)
        self.client_br_divisor_label.setText("Client BrDivisor:")
        self.client_br_divisor_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_br_divisor_edit.setFixedWidth(100)
        self.client_br_divisor_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_br_divisor))

        # client contrast(black level) adjust
        self.client_contrast_label = QLabel(self.mainwindow.right_frame)
        self.client_contrast_label.setText("Client Black-Lv:")
        self.client_contrast_edit = QLineEdit(self.mainwindow.right_frame)
        self.client_contrast_edit.setFixedWidth(100)
        self.client_contrast_edit.setText(
            str(self.mainwindow.media_engine.media_processor.video_params.frame_contrast))

        self.video_params_widget = QWidget(self.mainwindow.right_frame)
        video_params_layout = QGridLayout()
        self.video_params_widget.setLayout(video_params_layout)

        self.video_params_confirm_btn = QPushButton(self.mainwindow.right_frame)
        self.video_params_confirm_btn.setText("Set")
        self.video_params_confirm_btn.clicked.connect(self.video_params_confirm_btn_clicked)

        self.video_params_pinch_btn = QPushButton(self.mainwindow.right_frame)
        self.video_params_pinch_btn.setText("P5")
        self.video_params_pinch_btn.clicked.connect(self.video_params_pinch_btn_clicked)



        video_params_layout.addWidget(self.redgain_label, 0, 0)
        video_params_layout.addWidget(self.redgain_edit, 0, 1)
        video_params_layout.addWidget(self.greengain_label, 0, 2)
        video_params_layout.addWidget(self.greengain_edit, 0, 3)
        video_params_layout.addWidget(self.blugain_label, 0, 4)
        video_params_layout.addWidget(self.bluegain_edit, 0, 5)

        video_params_layout.addWidget(self.brightness_label, 1, 0)
        video_params_layout.addWidget(self.brightness_edit, 1, 1)
        video_params_layout.addWidget(self.contrast_label, 1, 2)
        video_params_layout.addWidget(self.contrast_edit, 1, 3)

        video_params_layout.addWidget(self.client_brightness_label, 2, 0)
        video_params_layout.addWidget(self.client_brightness_edit, 2, 1)
        video_params_layout.addWidget(self.client_br_divisor_label, 2, 2)
        video_params_layout.addWidget(self.client_br_divisor_edit, 2, 3)
        video_params_layout.addWidget(self.client_contrast_label, 3, 0)
        video_params_layout.addWidget(self.client_contrast_edit, 3, 1)

        video_params_layout.addWidget(self.video_params_pinch_btn, 3, 4)
        video_params_layout.addWidget(self.video_params_confirm_btn, 3, 5)

        if self.mainwindow.engineer_mode is True:
            self.max_brightness_label = QLabel(self.mainwindow.right_frame)
            self.max_brightness_label.setText( "Max Frame Brightness Value is " +
                str((256*int(self.client_brightness_edit.text()))/(int(self.client_br_divisor_edit.text())*100)))
            video_params_layout.addWidget(self.max_brightness_label, 4, 0, 1, 5)

    def stop_media_trigger(self):
        log.debug("")

    def pause_media_trigger(self):
        """check the popen subprocess is alive or not"""
        if self.mainwindow.media_engine.media_processor.play_status == play_status.playing:
            self.mainwindow.pause_media_set()
            self.btn_pause.setText("Resume")
        elif self.mainwindow.media_engine.media_processor.play_status == play_status.pausing:
            self.mainwindow.resume_media_set()
            self.btn_pause.setText("Pause")

    def repeat_option_trigger(self):
        if self.play_option_repeat >= repeat_option.repeat_option_max:
            self.play_option_repeat = repeat_option.repeat_none
        else:
            self.play_option_repeat += 1

        if self.play_option_repeat == repeat_option.repeat_none:
            self.btn_repeat.setText("No Repeat")
        elif self.play_option_repeat == repeat_option.repeat_one:
            self.btn_repeat.setText("Repeat One")
        elif self.play_option_repeat == repeat_option.repeat_random:
            self.btn_repeat.setText("Random")
        elif self.play_option_repeat == repeat_option.repeat_all:
            self.btn_repeat.setText("Repeat All")
        else:
            self.btn_repeat.setText("Repeat unknown")

        self.mainwindow.repeat_option_set(self.play_option_repeat)
        log.debug("self.play_option_repeat : %d", self.play_option_repeat)

    # right clicked slot function
    def menu_context_tree(self, position):
        widgetitem = self.file_tree.itemAt(position)
        self.right_clicked_pos = position
        if widgetitem.childCount() != 0:
            ''' parent 為 Playlist,表示自己為playlist之一'''
            if widgetitem.parent().text(0) == "Playlist":
                self.show_playlist_popMenu(self.file_tree.mapToGlobal(position))
                return
            log.debug("Just a label, not file list")
            return
        if widgetitem.parent() is not None:
            if widgetitem.parent().text(0) == "Internal Media":
                self.right_clicked_select_file_uri = internal_media_folder + "/" + widgetitem.text(0)
            elif widgetitem.parent().text(0) == "External Media":
                log.debug("%s", widgetitem.text(0))
                return
            elif "Playlist" in widgetitem.parent().text(0):
                self.show_playlist_popMenu(self.file_tree.mapToGlobal(position))
                return
            elif widgetitem.parent().parent() is not None:
                log.debug("%s", widgetitem.parent().parent().text(0))
                if "External Media" in widgetitem.parent().parent().text(0):
                    for external_medialist in self.media_engine.external_medialist:
                        if widgetitem.parent().text(0) in external_medialist.folder_uri:
                            for file_uri in external_medialist.filelist:
                                if widgetitem.text(0) in file_uri:
                                    self.right_clicked_select_file_uri = file_uri

                elif "Playlist" in widgetitem.parent().parent().text(0):
                    log.debug("no playlist right click")
                    # self.right_clicked_pos = position
                    self.show_playlist_file_pop_menu(self.file_tree.mapToGlobal(position))

                    return
        else:
            log.debug("root")
            return

        self.show_media_file_pop_menu(self.file_tree.mapToGlobal(position))

    def show_media_file_pop_menu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)

        play_act = QAction("Play", self)
        pop_menu.addAction(play_act)
        pop_menu.addSeparator()

        add_to_playlist_menu = QMenu('AddtoPlaylist')
        set_qstyle_dark(add_to_playlist_menu)

        for playlist in self.mainwindow.media_engine.playlist:
            playlist_name = playlist.name
            add_to_playlist_menu.addAction('add to ' + playlist_name)

        add_to_playlist_menu.addAction('add to new playlist')
        pop_menu.addMenu(add_to_playlist_menu)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(pos)

    '''處理playlist, 目前只有一個menu --> del'''

    def show_playlist_popMenu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)
        playact = QAction("Play Playlist", self)
        pop_menu.addAction(playact)
        remove_act = QAction("Remove Playlist", self)
        pop_menu.addAction(remove_act)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(pos)

    def show_playlist_file_pop_menu(self, pos):
        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)

        remove_act = QAction("Remove file from playlist", self)
        pop_menu.addAction(remove_act)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(pos)

    def pop_menu_trigger_act(self, q):
        log.debug("%s", q.text())
        if q.text() == "Play":
            """play single file"""
            log.debug("file_uri :%s", self.right_clicked_select_file_uri)
            self.media_engine.play_single_file(self.right_clicked_select_file_uri)
            '''self.ff_process = utils.ffmpy_utils.ffmpy_execute(self, self.right_clicked_select_file_uri, width=80, height=96)
            self.play_type = play_type.play_single'''
        elif "add to " in q.text():
            log.debug("media file uri : %s", self.right_clicked_select_file_uri)
            playlist_name = q.text().split(" ")[2]
            if playlist_name == 'new':
                #launch a dialog
                # pop up a playlist generation dialog
                if self.NewPlaylistDialog is None:
                    self.NewPlaylistDialog = NewPlaylistDialog(self.mainwindow.media_engine.playlist)
                self.NewPlaylistDialog.signal_new_playlist_generate.connect(self.mainwindow.slot_new_playlist)
                self.NewPlaylistDialog.show()
            else:
                self.mainwindow.media_engine.add_to_playlist(playlist_name, self.right_clicked_select_file_uri)
        elif q.text() == "Remove file from playlist":
            # log.debug("%s", self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y()).text(0))
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            parent = item.parent()
            remove_file_name = item.text(0)
            remove_from_playlist = parent.text(0)
            log.debug("remove_file_name : %s", remove_file_name)
            log.debug("remove_from_playlist : %s", remove_from_playlist)
            for i in range(parent.childCount()):
                if parent.child(i).text(0) == remove_file_name:
                    self.mainwindow.media_engine.remove_from_playlist(remove_from_playlist, i)
                    break
        elif q.text() == "Remove Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            remove_playlist_name = item.text(0)
            self.mainwindow.media_engine.del_playlist(remove_playlist_name)
        elif q.text() == "Play Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            play_playlist_name = item.text(0)
            self.mainwindow.media_engine.play_playlsit(play_playlist_name)

    def resfresh_video_params_config_file(self):
        log.debug("")
        self.media_engine.media_processor.video_params.refresh_config_file()

    def video_params_confirm_btn_clicked(self):
        media_processor = self.media_engine.media_processor
        video_params = media_processor.video_params
        if video_params.video_brightness != int(self.brightness_edit.text()):
            log.debug("brightness changed!")
            media_processor.set_brightness_level(int(self.brightness_edit.text()))
        if video_params.video_contrast != int(self.contrast_edit.text()):
            log.debug("contrast changed!")
            media_processor.set_contrast_level(int(self.contrast_edit.text()))
        if video_params.video_red_bias != int(self.redgain_edit.text()):
            log.debug("red gain changed!")
            media_processor.set_red_bias_level(int(self.redgain_edit.text()))
        if video_params.video_green_bias != int(self.greengain_edit.text()):
            log.debug("green gain changed!")
            media_processor.set_green_bias_level(int(self.greengain_edit.text()))
        if video_params.video_blue_bias != int(self.bluegain_edit.text()):
            log.debug("blue gain changed!")
            media_processor.set_blue_bias_level(int(self.bluegain_edit.text()))

        clients = self.mainwindow.clients
        if video_params.frame_brightness != int(self.client_brightness_edit.text()):
            video_params.frame_brightness = int(self.client_brightness_edit.text())
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_frame_brightness,
                           self.mainwindow.cmd_seq_id_increase(),
                            str(video_params.frame_brightness))

        if video_params.frame_br_divisor != int(self.client_br_divisor_edit.text()):
            video_params.frame_br_divisor = int(self.client_br_divisor_edit.text())
            for c in clients:
                c.send_cmd(cmd_set_frame_br_divisor,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_br_divisor))

        if video_params.frame_contrast != int(self.client_contrast_edit.text()):
            video_params.frame_contrast = int(self.client_contrast_edit.text())
            for c in clients:
                c.send_cmd(cmd_set_frame_contrast,
                           self.mainwindow.cmd_seq_id_increase(),
                           str(video_params.frame_contrast))

        if self.mainwindow.engineer_mode is True:
            self.refresh_max_brightness_label()

    def video_params_pinch_btn_clicked(self):
        log.debug("")
        clients = self.mainwindow.clients
        if self.video_params_pinch_btn.text() == "P5":
            self.video_params_pinch_btn.setText("P10")
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_pixel_interval,
                           self.mainwindow.cmd_seq_id_increase(),
                            str(1))
        else:
            self.video_params_pinch_btn.setText("P5")
            for c in clients:
                log.debug("c.client_ip = %s", c.client_ip)
                c.send_cmd(cmd_set_pixel_interval,
                           self.mainwindow.cmd_seq_id_increase(),
                            str(0))

    def refresh_max_brightness_label(self):
        if self.mainwindow.engineer_mode is False:
            return
        self.max_brightness_label.setText("Max Frame Brightness Value is " +
                                          str((256 * int(self.client_brightness_edit.text())) / (
                                                      int(self.client_br_divisor_edit.text()) * 100)))