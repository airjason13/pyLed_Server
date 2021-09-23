import os.path

from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject
from utils.ffmpy_utils import *
import utils.log_utils
from utils.file_utils import *
from pyudev import Context, Monitor, MonitorObserver

log = utils.log_utils.logging_init(__file__)

class media_engine(QObject):
    ''' changed_or_not, playlist_name, file_uri, "add" or "del" '''
    signal_playlist_changed_ret = pyqtSignal(bool, str, str, int, str)
    ''' changed_or_not '''
    signal_external_medialist_changed_ret = pyqtSignal(bool)

    '''Action TAG'''
    ACTION_TAG_ADD_MEDIA_FILE="add_media_file"
    ACTION_TAG_REMOVE_MEDIA_FILE="remove_media_file"
    ACTION_TAG_REMOVE_ENTIRE_PLAYLIST="remove_entire_playlist"
    ACTION_TAG_ADD_NEW_PLAYLIST="add_playlist"

    '''init'''
    def __init__(self, **kwargs):
        super(media_engine, self).__init__(**kwargs)
        self.internal_medialist = medialist(internal_media_folder)

        ''' handle the external media list'''
        #self.external_mount_points = get_mount_points()
        self.external_medialist = []
        for mount_point in utils.file_utils.get_mount_points():
            external_medialist_tmp = medialist(mount_point)
            self.external_medialist.append(external_medialist_tmp)


        '''handle the playlist'''
        self.playlist_files = get_playlist_file_list(internal_media_folder + PlaylistFolder)
        log.debug(self.playlist_files)
        self.playlist = []
        for file in self.playlist_files:
            playlist_tmp = playlist(file)
            self.playlist.append(playlist_tmp)


        '''init usb monitor'''
        self.init_usb_monitor()


    def init_usb_monitor(self):
        context = Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        observer = MonitorObserver(monitor, callback=self.print_device_event, name='monitor-observer')
        observer.daemon
        observer.start()

    def add_external_medialist(self, uri):
        log.debug("uri : %s", uri)
        for external_media_list in self.external_medialist:
            if external_media_list.folder_uri == uri:
                log.debug("already have this one!")
                return

        external_media_list = medialist(uri)
        self.external_medialist.append(external_media_list)



    def add_to_playlist(self, playlist_name, media_file_uri):
        log.debug("playlist_name : %s", playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0, self.ACTION_TAG_ADD_MEDIA_FILE)
                return

        '''在這邊表示playlist_name 為新創建的,不在原本的playlist array裏面'''
        self.new_playlist(playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0, self.ACTION_TAG_ADD_NEW_PLAYLIST)
                return


    def remove_from_playlist(self, playlist_name, index):
        log.debug("remove_from_playlist index :%d", index)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                for i in playlist.fileslist:
                    log.debug("%s", i)
                media_file_uri = playlist.fileslist[index]
                del playlist.fileslist[index]
                playlist.playlist_sync_file()
                for i in playlist.fileslist:
                    log.debug("%s", i)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, index, self.ACTION_TAG_REMOVE_MEDIA_FILE)


    def print_device_event(self, device):
        sleep(3)  # time for waiting mount
        mount_points = get_mount_points()
        '''用mount points 長度判斷是否要改變external_medialist'''
        if len(mount_points) != len(self.external_medialist):
            '''全砍了,再創新的'''
            del self.external_medialist
            self.external_medialist = []
            for uri in mount_points:
                log.debug("uri : %s", uri)
                self.add_external_medialist(uri)
            self.signal_external_medialist_changed_ret.emit(True)

    def new_playlist(self, new_playlist_name):
        #new_playlist_name += ".playlist"
        new_playlist = playlist(internal_media_folder + PlaylistFolder + new_playlist_name)
        new_playlist.playlist_sync_file()
        self.playlist.append(new_playlist)

    def del_playlist(self, remove_playlist_name):
        index = -1
        playlist_len = len(self.playlist)
        log.debug("playlist_len : %d", playlist_len)
        for i in range(playlist_len):
            if self.playlist[i].name == remove_playlist_name:
                index = i
                break

        if index != -1:
            self.playlist[i].del_playlist_file()
            del self.playlist[index]
            self.signal_playlist_changed_ret.emit(True, remove_playlist_name, "", 0, self.ACTION_TAG_REMOVE_ENTIRE_PLAYLIST)



class medialist(QObject):
    def __init__(self, uri):
        self.folder_uri = uri
        self.filelist = utils.file_utils.get_media_file_list(self.folder_uri)


class playlist(QObject):
    def __init__(self, name):
        self.name_with_path = name
        self.name = os.path.basename(self.name_with_path)
        self.fileslist = []
        if os.path.exists(self.name_with_path):
            self.load_playlist(self.name_with_path)
        else:
            self.add_file_uri_to_playlist(None)

    def load_playlist(self, file_uri):
        file = open(file_uri, 'r')
        lines = file.readlines()
        for line in lines:
            if len(line) > 1:
                self.fileslist.append(line.strip())

    def add_file_uri_to_playlist(self, file_uri):
        if file_uri is not None:
            self.fileslist.append(file_uri)
            self.playlist_sync_file()
        else:
            file = open(self.name_with_path, "w")
            file.truncate()

    def playlist_sync_file(self):
        file = open(self.name_with_path, "w")
        for i in self.fileslist:
            file.write(i + "\n")
        file.truncate()

    def del_playlist_file(self):
        if os.path.exists(self.name_with_path):
            os.remove(self.name_with_path)

    def __del__(self):
        log.debug("playlist del")

