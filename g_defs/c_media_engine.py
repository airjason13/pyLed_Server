import os.path
import signal
import time
import threading
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer
from utils.ffmpy_utils import *
import utils.log_utils
from utils.file_utils import *
from pyudev import Context, Monitor, MonitorObserver
from g_defs.c_video_params import *
import random

log = utils.log_utils.logging_init(__file__)


class media_engine(QObject):
    ''' changed_or_not, playlist_name, file_uri, "add" or "del" '''
    signal_playlist_changed_ret = pyqtSignal(bool, str, str, int, str)
    ''' changed_or_not '''
    signal_external_medialist_changed_ret = pyqtSignal(bool)

    '''Action TAG'''
    ACTION_TAG_ADD_MEDIA_FILE = "add_media_file"
    ACTION_TAG_REMOVE_MEDIA_FILE = "remove_media_file"
    ACTION_TAG_REMOVE_ENTIRE_PLAYLIST = "remove_entire_playlist"
    ACTION_TAG_ADD_NEW_PLAYLIST = "add_playlist"

    '''init'''

    def __init__(self, **kwargs):
        super(media_engine, self).__init__(**kwargs)
        self.internal_medialist = medialist(internal_media_folder)

        ''' handle the external media list'''
        # self.external_mount_points = get_mount_points()
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

        '''media_process'''
        self.media_processor = media_processor()

        '''hdmi-in cast'''

    # hdmi_in_src : string
    # cast_dst : array of string
    def start_hdmi_in_v4l2(self, hdmi_in_src, cast_dst):
        log.debug("")
        if os.path.exists(hdmi_in_src) is False:
            log.error("%s is not exist", hdmi_in_src)
            return None
        return self.media_processor.hdmi_in_cast_v4l2(hdmi_in_src, cast_dst)

    def start_hdmi_in_h264(self, hdmi_in_src, cast_dst):
        log.debug("")
        if os.path.exists(hdmi_in_src) is False:
            log.error("%s is not exist", hdmi_in_src)
            return None
        return self.media_processor.hdmi_in_cast_h264(hdmi_in_src, cast_dst)

    def play_single_file(self, file_uri):
        log.debug("")
        self.stop_play()
        if os.path.exists(file_uri) is False:
            log.error("%s is not exist", file_uri)
        self.media_processor.single_play(file_uri)

    def play_playlsit(self, playlist_name):
        log.debug("playlist_name = %s", playlist_name)
        self.stop_play()
        for pl in self.playlist:
            if pl.name == playlist_name:
                log.debug("find playlist with playlist_name = %s", playlist_name)
                self.media_processor.playlist_play(pl)

    def stop_play(self):
        self.media_processor.stop_playing()

    def pause_play(self):
        self.media_processor.pause_playing()

    def resume_play(self):
        self.media_processor.resume_playing()

    def init_usb_monitor(self):
        context = Context()
        monitor = Monitor.from_netlink(context)
        monitor.filter_by(subsystem='usb')
        observer = MonitorObserver(monitor,
                                   callback=self.print_device_event,
                                   name='monitor-observer')
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
        playlist_folder_path = internal_media_folder + "/.playlists"
        if not os.path.exists(playlist_folder_path):
            os.makedirs(playlist_folder_path)

        log.debug("playlist_name : %s", playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0,
                                                      self.ACTION_TAG_ADD_MEDIA_FILE)
                return

        '''在這邊表示playlist_name 為新創建的,不在原本的playlist array裏面'''
        self.new_playlist(playlist_name)
        for playlist in self.playlist:
            if playlist.name == playlist_name:
                playlist.add_file_uri_to_playlist(media_file_uri)
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, 0,
                                                      self.ACTION_TAG_ADD_NEW_PLAYLIST)
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
                self.signal_playlist_changed_ret.emit(True, playlist_name, media_file_uri, index,
                                                      self.ACTION_TAG_REMOVE_MEDIA_FILE)

    def print_device_event(self, device):
        sleep(3)  # time for waiting mount
        mount_points = get_mount_points()
        '''用mount points 長度判斷是否要改變external_medialist'''
        if len(mount_points) != len(self.external_medialist):
            del self.external_medialist
            self.external_medialist = []
            for uri in mount_points:
                log.debug("uri : %s", uri)
                self.add_external_medialist(uri)
            self.signal_external_medialist_changed_ret.emit(True)

    def new_playlist(self, new_playlist_name):
        # new_playlist_name += ".playlist"
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
            self.playlist[index].del_playlist_file()
            del self.playlist[index]
            self.signal_playlist_changed_ret.emit(True, remove_playlist_name, "", 0,
                                                  self.ACTION_TAG_REMOVE_ENTIRE_PLAYLIST)

    def refresh_internal_medialist(self):
        del self.internal_medialist
        self.internal_medialist = medialist(internal_media_folder)

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
        log.debug("del_playlist_file")
        if os.path.exists(self.name_with_path):
            log.debug("del playlist : %s", self.name_with_path)
            os.remove(self.name_with_path)

    def __del__(self):
        log.debug("playlist del")


class media_processor(QObject):
    signal_media_play_status_changed = pyqtSignal(bool, int)
    signal_play_hdmi_in_start_ret = pyqtSignal()
    signal_play_hdmi_in_finish_ret = pyqtSignal()

    def __init__(self):
        super(media_processor, self).__init__()
        self.output_width = default_led_wall_width
        self.output_height = default_led_wall_height
        self.play_status = play_status.stop
        self.pre_play_status = play_status.stop
        self.play_type = play_type.play_none
        self.repeat_option = repeat_option.repeat_all
        self.play_single_file_thread = None
        self.ffmpy_process = None
        self.playing_file_name = None
        self.video_params = video_params(True, 20, 50, 0, 0, 0, 0)

        self.check_ffmpy_process_timer = QTimer(self)
        self.check_ffmpy_process_timer.timeout.connect(self.check_ffmpy_process)  # 當時間到時會執行 run
        self.check_ffmpy_process_timer.start(1000)

        self.check_play_status_timer = QTimer(self)
        self.check_play_status_timer.timeout.connect(self.check_play_status)  # 當時間到時會執行 run
        self.check_play_status_timer.start(500)

        self.play_single_file_worker = None
        self.play_playlist_worker = None
        self.play_hdmi_in_worker = None

        ''' this is only cast /dev/video0 to others for preview'''
        self.hdmi_in_cast_process = None

    def set_repeat_option(self, option):
        if option < repeat_option.repeat_none \
                or option > repeat_option.repeat_option_max:
            log.error("repeat_option out of range")
            return
        self.repeat_option = option
        log.debug("self.repeat_option : %d", self.repeat_option)

    def set_output_resolution(self, width, height):
        self.output_width = width
        self.output_height = height

    def stop_playing(self):
        log.debug("")
        if self.play_status != play_status.stop:
            try:
                if self.ffmpy_process is not None:
                    os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                if self.play_single_file_worker is not None:
                    self.play_single_file_worker.stop()
                if self.play_playlist_worker is not None:
                    self.play_playlist_worker.stop()
                if self.play_hdmi_in_worker is not None:
                    self.play_hdmi_in_worker.stop()
            except Exception as e:
                log.debug(e)

    def pause_playing(self):
        if self.play_status != play_status.stop:
            try:
                if self.ffmpy_process is not None:
                    os.kill(self.ffmpy_process.pid, signal.SIGSTOP)
                    self.play_status = play_status.pausing
            except Exception as e:
                log.debug(e)

    def resume_playing(self):
        if self.play_status != play_status.stop:
            try:
                if self.ffmpy_process is not None:
                    os.kill(self.ffmpy_process.pid, signal.SIGCONT)
                    self.play_status = play_status.playing
            except Exception as e:
                log.debug(e)

    def single_play(self, file_uri):
        log.debug("")

        if self.play_single_file_worker is not None:
            if self.play_single_file_worker.get_task_status() == 1:
                self.stop_playing()
                self.play_single_file_worker.stop()
                self.play_single_file_thread.quit()
                self.play_single_file_thread.wait()

        self.play_single_file_thread = QThread()
        self.play_single_file_worker = self.play_single_file_work(self, file_uri, 5)
        self.play_single_file_worker.moveToThread(self.play_single_file_thread)
        self.play_single_file_thread.started.connect(self.play_single_file_worker.run)
        self.play_single_file_worker.finished.connect(self.play_single_file_thread.quit)
        self.play_single_file_worker.finished.connect(self.play_single_file_worker.deleteLater)
        self.play_single_file_thread.finished.connect(self.play_single_file_thread.deleteLater)
        self.play_single_file_thread.start()

    def playlist_play(self, playlist):
        log.debug("")
        # if self.play_status == play_status.playing:
        #    os.kill(self.ff_process.pid, signal.SIGTERM)

        if self.play_playlist_worker is not None:
            if self.play_playlist_worker.get_task_status() == 1:
                self.stop_playing()
                self.play_playlist_worker.stop()
                self.play_playlist_worker.quit()
                self.play_playlist_worker.wait()

        self.play_playlist_thread = QThread()
        self.play_playlist_worker = self.play_playlist_work(self, playlist, 5)
        self.play_playlist_worker.moveToThread(self.play_playlist_thread)
        self.play_playlist_thread.started.connect(self.play_playlist_worker.run)
        self.play_playlist_worker.finished.connect(self.play_playlist_thread.quit)
        self.play_playlist_worker.finished.connect(self.play_playlist_worker.deleteLater)
        self.play_playlist_thread.finished.connect(self.play_playlist_thread.deleteLater)
        self.play_playlist_thread.start()

    def hdmi_in_play(self, video_src, video_dst):
        log.debug("%s", video_dst)

        if self.play_hdmi_in_worker is not None:
            if self.play_hdmi_in_worker.get_task_status() == 1:
                self.stop_playing()
                self.play_hdmi_in_worker.stop()
                self.play_hdmi_in_worker.quit()
                self.play_hdmi_in_worker.wait()

        if self.play_hdmi_in_thread is not None:
            self.play_hdmi_in_thread.finished()
            self.play_hdmi_in_thread.deleteLater()

        self.play_hdmi_in_thread = QThread()
        self.play_hdmi_in_worker = self.play_hdmi_in_work(self, video_src, video_dst)
        self.play_hdmi_in_worker.signal_play_hdmi_in_start.connect(self.play_hdmi_in_start_ret)
        self.play_hdmi_in_worker.signal_play_hdmi_in_finish.connect(self.play_hdmi_in_finish_ret)
        self.play_hdmi_in_worker.moveToThread(self.play_hdmi_in_thread)
        self.play_hdmi_in_thread.started.connect(self.play_hdmi_in_worker.run)
        self.play_hdmi_in_worker.finished.connect(self.play_hdmi_in_thread.quit)
        self.play_hdmi_in_worker.finished.connect(self.play_hdmi_in_worker.deleteLater)
        self.play_hdmi_in_thread.finished.connect(self.play_hdmi_in_thread.deleteLater)
        self.play_hdmi_in_thread.start()

    def play_hdmi_in_start_ret(self):
        self.signal_play_hdmi_in_start_ret.emit()

    def play_hdmi_in_finish_ret(self):
        self.signal_play_hdmi_in_finish_ret.emit()

    def hdmi_in_cast_h264(self, hdmi_in_src, cast_dst):
        self.hdmi_in_cast_process = \
            neo_ffmpy_cast_video_h264(hdmi_in_src, cast_dst,
                              self.video_params.get_translated_brightness(),
                              self.video_params.get_translated_contrast(),
                              self.video_params.get_translated_redgain(),
                              self.video_params.get_translated_greengain(),
                              self.video_params.get_translated_bluegain(),
                              160,
                              120 )
                              #self.output_width,
                              #self.output_height )
        log.debug("self.hdmi_in_cast_process.pid = %d", self.hdmi_in_cast_process.pid)
        return self.hdmi_in_cast_process


    def hdmi_in_cast_v4l2(self, hdmi_in_src, cast_dst):
        self.hdmi_in_cast_process = \
            neo_ffmpy_cast_video_v4l2(hdmi_in_src, cast_dst,
                              self.video_params.get_translated_brightness(),
                              self.video_params.get_translated_contrast(),
                              self.video_params.get_translated_redgain(),
                              self.video_params.get_translated_greengain(),
                              self.video_params.get_translated_bluegain(),
                              self.output_width,
                              self.output_height )
        #log.debug("self.hdmi_in_cast_process.pid = %d", self.hdmi_in_cast_process.pid)
        return self.hdmi_in_cast_process

    '''檢查影片是否推播完畢'''
    def check_ffmpy_process(self):
        if self.ffmpy_process is None:
            return
        try:
            if self.ffmpy_process.poll() is None:
                # log.debug("ffmpy_process alive!")
                # os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                pass
            else:
                log.debug("poll() not None!")
                if self.play_status != play_status.stop:
                    self.play_status = play_status.stop
                    self.ffmpy_process = None
                    self.playing_file_name = None

        except Exception as e:
            log.debug(e)

    def check_play_status(self):
        if self.play_status != self.pre_play_status:
            pass

    def set_brightness_level(self, level):
        self.video_params.set_video_brightness(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('brightness', self.video_params.get_translated_brightness())

    def set_contrast_level(self, level):
        self.video_params.set_video_contrast(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('contrast', self.video_params.get_translated_contrast())

    def set_red_bias_level(self, level):
        self.video_params.set_video_red_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('red_gain', self.video_params.get_translated_redgain())

    def set_green_bias_level(self, level):
        self.video_params.set_video_green_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('green_gain', self.video_params.get_translated_greengain())

    def set_blue_bias_level(self, level):
        self.video_params.set_video_blue_bias(level)
        if self.ffmpy_process is not None:
            ffmpy_set_video_param_level('blue_gain', self.video_params.get_translated_bluegain())

    def set_image_period_value(self, value):
        self.video_params.set_image_peroid(value)

    class play_playlist_work(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)

        def __init__(self, QObject, plist, n):
            super().__init__()
            self.media_processor = QObject
            self.playlist = plist
            self.n = n
            self.force_stop = False
            self.worker_status = 0
            self.file_idx = 0

        def run(self):
            log.debug("self.media_processor.repeat_option : %d", self.media_processor.repeat_option)
            self.media_processor.play_type = play_type.play_playlist
            self.file_idx = 0
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            if self.media_processor.play_status == play_status.pausing:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                        os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                        # time.sleep(1)
                        log.debug("kill")
                    except Exception as e:
                        log.debug(e)
                if self.media_processor.repeat_option == repeat_option.repeat_random:
                    self.file_idx = random.randint(0, len(self.playlist.fileslist) - 1)
                log.debug("file_idx = %d", self.file_idx)
                self.file_uri = self.playlist.fileslist[self.file_idx]
                if os.path.exists(self.file_uri) is False:
                    self.file_idx += 1
                    if self.file_idx >= len(self.playlist.fileslist):
                        if self.media_processor.repeat_option != repeat_option.repeat_one:
                            log.debug("Quit Play Playlist")
                            break
                        else:
                            self.file_idx = 0
                    continue

                log.debug("self.file_uri = %s", self.file_uri)
                self.media_processor.ffmpy_process = \
                    neo_ffmpy_execute(self.file_uri,
                                      self.media_processor.video_params.get_translated_brightness(),
                                      self.media_processor.video_params.get_translated_contrast(),
                                      self.media_processor.video_params.get_translated_redgain(),
                                      self.media_processor.video_params.get_translated_greengain(),
                                      self.media_processor.video_params.get_translated_bluegain(),
                                      self.media_processor.video_params.image_period,
                                      self.media_processor.output_width,
                                      self.media_processor.output_height)
                if self.media_processor.ffmpy_process.pid > 0:
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.file_uri
                    while True:
                        if self.media_processor.play_status == play_status.stop:
                            break
                        if self.force_stop is True:
                            log.debug("force_stop first")
                            break
                        time.sleep(0.5)

                if self.force_stop is True:
                    log.debug("force_stop second")
                    break
                self.file_idx += 1
                if self.file_idx >= len(self.playlist.fileslist):
                    self.file_idx = 0
                    if self.media_processor.repeat_option == repeat_option.repeat_all or self.media_processor.repeat_option == repeat_option.repeat_random:
                        pass
                    else:
                        log.debug("self.media_processor.repeat_option : %d", self.media_processor.repeat_option)
                        log.debug("Quit Play Playlist After all file done")
                        break
                else:
                    pass
            self.finished.emit()
            self.worker_status = 0
            self.media_processor.play_type = play_type.play_none

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status

    class play_single_file_work(QObject):
        finished = pyqtSignal()
        progress = pyqtSignal(int)


        def __init__(self, QObject, file_uri, n):
            super().__init__()
            self.media_processor = QObject
            self.file_uri = file_uri
            self.n = n
            self.force_stop = False
            self.worker_status = 0

        def run(self):
            self.media_processor.play_type = play_type.play_single
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            if self.media_processor.play_status == play_status.pausing:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                        os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                        # time.sleep(1)
                        log.debug("kill")
                    except Exception as e:
                        log.debug(e)

                log.debug("test")
                self.media_processor.ffmpy_process = \
                    neo_ffmpy_execute(self.file_uri,
                       self.media_processor.video_params.get_translated_brightness(),
                       self.media_processor.video_params.get_translated_contrast(),
                       self.media_processor.video_params.get_translated_redgain(),
                       self.media_processor.video_params.get_translated_greengain(),
                       self.media_processor.video_params.get_translated_bluegain(),
                       self.media_processor.video_params.image_period,
                       self.media_processor.output_width,
                       self.media_processor.output_height)
                if self.media_processor.ffmpy_process.pid > 0:
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.file_uri
                    while True:
                        if self.media_processor.play_status == play_status.stop:
                            break
                        if self.force_stop is True:
                            break
                        time.sleep(0.5)

                if self.media_processor.repeat_option != repeat_option.repeat_one:
                    break
                if self.force_stop is True:
                    break

            self.finished.emit()
            self.media_processor.play_type = play_type.play_none
            self.worker_status = 0

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status

    class play_hdmi_in_work(QObject):
        signal_play_hdmi_in_finish = pyqtSignal()
        signal_play_hdmi_in_start = pyqtSignal()
        def __init__(self, QObject, video_src, cast_dst):
            super().__init__()
            self.media_processor = QObject
            self.video_src = video_src
            self.cast_dst = cast_dst
            log.debug("cast_dst :%s", cast_dst)
            self.force_stop = False
            self.worker_status = 0
        def run(self):
            self.media_processor.play_type = play_type.play_hdmi_in
            while True:
                self.worker_status = 1
                if self.media_processor.play_status != play_status.stop:
                    ''' kill other streaming ffmpy instance first'''
                    try:
                        if self.media_processor.ffmpy_process is not None:
                            if self.media_processor.play_status == play_status.pausing:
                                os.kill(self.media_processor.ffmpy_process.pid, signal.SIGCONT)
                                # time.sleep(1)
                        os.kill(self.ffmpy_process.pid, signal.SIGTERM)
                        # time.sleep(1)
                        log.debug("kill")
                    except Exception as e:
                        log.debug(e)


                self.media_processor.ffmpy_process = \
                    neo_ffmpy_cast_video_h264(self.video_src, self.cast_dst, 
                       self.media_processor.video_params.get_translated_brightness(),
                       self.media_processor.video_params.get_translated_contrast(),
                       self.media_processor.video_params.get_translated_redgain(),
                       self.media_processor.video_params.get_translated_greengain(),
                       self.media_processor.video_params.get_translated_bluegain(),
                       self.media_processor.output_width,
                       self.media_processor.output_height)
                if self.media_processor.ffmpy_process.pid > 0:
                    self.signal_play_hdmi_in_start.emit()
                    self.media_processor.play_status = play_status.playing
                    self.media_processor.playing_file_name = self.video_src
                    while True:
                        if self.media_processor.play_status == play_status.stop:
                            break
                        if self.force_stop is True:
                            break
                        time.sleep(0.5)

                if self.media_processor.repeat_option != repeat_option.repeat_one:
                    break
                if self.force_stop is True:
                    break

            self.signal_play_hdmi_in_finish.emit()
            self.media_processor.play_type = play_type.play_none
            self.worker_status = 0

        def stop(self):
            self.force_stop = True

        def get_task_status(self):
            return self.worker_status
