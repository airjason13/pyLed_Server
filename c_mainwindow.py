# coding=UTF-8
import os
from time import sleep
import qthreads.c_alive_report_thread

import utils.ffmpy_utils
import utils.file_utils
import utils.log_utils
import utils.net_utils as net_utils
import utils.qtui_utils
import utils.update_utils
import utils.astral_utils
from c_cabinet_setting_window import CabinetSettingWindow
from c_led_layout_window import LedLayoutWindow
from g_defs.c_cabinet_params import cabinet_params
from g_defs.c_client import client
from g_defs.c_filewatcher import *
from g_defs.c_lcd1602 import *
from g_defs.c_led_config import *
from g_defs.c_media_engine import media_engine
from pyqt_worker import Worker
from qtui.c_page_client import *
from qtui.c_page_hdmi_in import *
from qtui.c_page_cms import *
from qtui.c_page_medialist import *
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject
from str_define import *
from g_defs.c_bluetooth import BlueTooth
from datetime import datetime
import pytz
from astral_hashmap import *
from qlocalmessage import send_message
from qt_web_comunication import *
log = utils.log_utils.logging_init(__file__)
from zoneinfo import ZoneInfo

class MainUi(QMainWindow):
    signal_add_cabinet_label = pyqtSignal(cabinet_params)

    signal_redraw_cabinet_label = pyqtSignal(cabinet_params, Qt.GlobalColor)

    signal_right_page_changed = pyqtSignal(int, int)  # pre_idx, current_idx

    option_btn_width = 240
    option_btn_height = 60

    def __init__(self):
        super().__init__()
        pg.setConfigOptions(antialias=True)

        #keep the screen on for cms
        keep_screen_alive = os.popen("xset s off -dpms")
        keep_screen_alive.close()

        self.center()
        self.setWindowOpacity(1.0)  # 窗口透明度
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.led_config = Led_Config()
        # self.led_config.get_led_wall_width()
        # self.led_config.set_led_wall_res(888,666)

        self.web_cmd_mutex = QMutex()

        # insert v4l2loopback module first
        if os.path.exists("/dev/video5") and os.path.exists("/dev/video6"):
            pass
        else:
            os.system('echo %s | sudo -S %s' % ("workout13", "modprobe v4l2loopback video_nr=3,4,5,6"))

        # set engineer mode trigger
        # self.engineer_mode_trigger = QShortcut(QKeySequence("Ctrl+E"), self)
        # self.engineer_mode_trigger.activated.connect(self.ctrl_e_trigger)
        self.engineer_mode = False

        # instance elements
        self.NewPlaylistDialog = None
        self.movie = None
        self.media_preview_widget = None
        self.right_frame = None
        self.right_layout = None
        self.splitter1 = None
        self.splitter2 = None

        # for get client ip in client page right click
        self.right_click_select_client_ip = None

        self.client_page = None
        self.medialist_page = None
        self.hdmi_in_page = None
        self.led_setting = None

        '''Initial media engine'''
        self.media_engine = media_engine(self.led_config)

        ''' Set Led layout params'''
        self.led_wall_width = self.led_config.get_led_wall_width()  # default_led_wall_width
        self.led_wall_height = self.led_config.get_led_wall_height()  # default_led_wall_height
        self.led_wall_brightness = default_led_wall_brightness
        self.led_cabinet_width = default_led_cabinet_width
        self.led_cabinet_height = default_led_cabinet_height

        self.led_layout_window = LedLayoutWindow(self.led_wall_width, self.led_wall_height,
                                                 self.led_cabinet_width, self.led_cabinet_height,
                                                 default_led_wall_margin)
        self.signal_add_cabinet_label.connect(self.led_layout_window.add_cabinet_label)
        self.signal_redraw_cabinet_label.connect(self.led_layout_window.redraw_cabinet_label)

        self.cabinet_setting_window = CabinetSettingWindow(None)
        self.cabinet_setting_window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.cabinet_setting_window.signal_set_cabinet_params.connect(self.set_cabinet_params)
        self.cabinet_setting_window.signal_draw_temp_cabinet.connect(self.draw_cabinet_label)
        self.cabinet_setting_window.signal_set_default_cabinet_resolution.connect(self.set_default_cabinet_resolution)
        self.client_led_layout = []

        '''main ui right frame page index'''
        self.page_idx = 0
        self.pre_page_idx = 0

        # initial streaming ffmpy status
        self.ffmpy_running = play_status.stop
        self.play_type = play_type.play_none
        self.ff_process = None
        self.play_option_repeat = repeat_option.repeat_all
        import routes
        routes.route_set_repeat_option(self.play_option_repeat)
        # font_size_config_file = open(internal_media_folder + SubtitleFolder + subtitle_size_file_name, 'r')
        # font_size = font_size_config_file.readline()
        font_size = utils.file_utils.get_text_size()
        routes.route_set_text_size(font_size)
        # font_size_config_file.close()
        # config_file = open(internal_media_folder + SubtitleFolder + subtitle_file_name, 'r')
        # content_line = config_file.readline()
        content_line = utils.file_utils.get_text_content()
        log.debug("content_line:%s", content_line)
        routes.route_set_text_content(content_line)
        # config_file.close()

        # get eth0 ip and set it to server_ip
        self.server_ip = net_utils.get_ip_address()
        self.clients = []
        self.clients_mutex = QMutex()
        ''' for check cmd seq '''
        self.cmd_send_seq_id = 0
        self.cmd_seq_id_mutex = QMutex()

        self.client_id_count = 0

        self.setMouseTracking(True)
        self.init_ui()
        self.page_status = self.statusBar()
        self.page_status.showMessage("Client Page")

        self.setWindowTitle("LED Server")
        
        self.client_reboot_flags = False

        self.broadcast_thread = \
            Worker(method=self.server_broadcast, data=server_broadcast_message, port=server_broadcast_port)
        self.broadcast_thread.start()
        self.refresh_clients_thread = Worker(method=self.refresh_clients_list, sleep_time=5)
        self.refresh_clients_thread.start()

        self.client_alive_report_thread = \
            qthreads.c_alive_report_thread.alive_report_thread(ip=self.server_ip, port=alive_report_port)
        self.client_alive_report_thread.check_client.connect(self.check_client)
        # self.client_alive_report_thread.signal_kill_ffmpy.connect(self.kill_ffmpy_process)
        self.client_alive_report_thread.start()

        self.preview_file_name = ""

        self.send_cmd_fail_msg = QMessageBox()

        self.media_engine.signal_playlist_changed_ret.connect(self.playlist_changed)
        self.media_engine.signal_external_medialist_changed_ret.connect(self.external_medialist_changed)
        self.media_engine.signal_play_status_changed.connect(self.play_status_changed)

        paths = [internal_media_folder]
        self.filewatcher = FileWatcher(paths)
        self.filewatcher.install_folder_changed_slot(self.internaldef_medialist_changed)

        # v4l2loopback variable
        self.v4l2loopback_module_probed = False

        if self.v4l2loopback_module_probed is False:
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                cmd = "modprobe v4l2loopback video_nr=3,4,5,6"
                os.system(cmd)
            else :
                # please modprobe v4l2loopback on x86 yourself
                pass
            self.v4l2loopback_module_probed = True

        self.signal_right_page_changed.connect(self.right_page_change_index)

        self.lcd1602 = LCD1602("LCD_TAG_VERSION_INFO", "LED SERVER", version, 5000)
        self.lcd1602.start()

        for i in range(5):
            # initial subtitle_blank.jpg
            try:
                ori_text_blank_jpg_uri = internal_media_folder + SubtitleFolder + subtitle_blank_jpg
                neo_text_blank_jpg_uri = internal_media_folder + subtitle_blank_jpg
                log.debug("%d", self.led_wall_width)
                log.debug("%d", self.led_wall_height)
                utils.ffmpy_utils.neo_ffmpy_scale(ori_text_blank_jpg_uri, neo_text_blank_jpg_uri,
                                                  self.led_wall_width, self.led_wall_height)
            except Exception as e:
                log.debug(e)
            if utils.ffmpy_utils.check_media_res(neo_text_blank_jpg_uri, self.led_wall_width, self.led_wall_height):
                log.debug("neo_text_blank_jpg_uri check ok!")
                break

        log.debug("self.geo x : %d", self.geometry().x())
        log.debug("self.geo y : %d", self.geometry().y())
        self.page_ui_mutex = QMutex()

        utils.file_utils.find_ffmpeg_process()
        utils.file_utils.kill_all_ffmpeg_process()

        self.bt_handle = BlueTooth()
        self.bt_handle.start()

        self.sleep_start_time, self.sleep_end_time = utils.file_utils.get_sleep_time_from_file()
        log.debug("self.sleep_start_time = %s", self.sleep_start_time)
        log.debug("self.sleep_end_time = %s", self.sleep_end_time)
        self.i_sleep_start_time_hour = int(self.sleep_start_time.split(":")[0])
        self.i_sleep_start_time_min = int(self.sleep_start_time.split(":")[1])
        self.i_sleep_end_time_hour = int(self.sleep_end_time.split(":")[0])
        self.i_sleep_end_time_min = int(self.sleep_end_time.split(":")[1])

        self.date_timer = QTimer(self)
        self.date_timer.timeout.connect(self.check_brightness_by_date_timer)
        # self.date_timer.start(1*60*1000)
        self.date_timer.start(1 * 60 * 1000)

        # reboot flag
        self.reboot_mode = utils.file_utils.get_reboot_mode_default_from_file()
        log.debug("self.reboot_mode = %s", self.reboot_mode)
        self.reboot_time = utils.file_utils.get_reboot_time_default_from_file()
        log.debug("self.reboot_time = %s", self.reboot_time)
        self.client_check_reboot_timer = QTimer(self)
        self.client_check_reboot_timer.timeout.connect(self.client_reboot_timer)
        # set one miniute timer
        self.client_check_reboot_timer.start(1 * 60 * 1000)
        
        '''self.dmesg_timer = QTimer(self)
        self.dmesg_timer.timeout.connect(self.check_dmesg)
        self.dmesg_timer.start(5 * 1000)'''

        # utils.astral_utils.get_sun_times("KK")
        self.city = City_Map[self.media_engine.media_processor.video_params.get_target_city_index()].get("City")
        # for test
        self.brightness_test_log = False

        # QTimer.singleShot(5000, self.demo_start_playlist)
        QTimer.singleShot(5000, self.demo_start_hdmi_in)
        # QTimer.singleShot(5000, self.demo_start_cms)

        self.web_cmd_time = time.time()
        self.tmp_clients_count = 0
        self.force_kill_ffmpy_count = 0

        self.test_count = 0

    def check_dmesg(self):
        # log.debug("dmesg")
        dmesg_res = os.popen("dmesg | grep mutex").read()
        if len(dmesg_res) != 0:
            log.debug("#######found error############")
            os.popen("reboot")


    def check_daymode_nightmode(self, sunrise_time, sunset_time, now):
        if self.brightness_test_log is True:
            file_uri = os.getcwd() + "/test_log.dat"
            f = open(file_uri, "a+")

        if sunrise_time < now < sunset_time:
            if self.brightness_test_log is True:
                log.debug("day mode")

            # log.debug("day_mode_brightness = %d", day_mode_brightness)
            if self.media_engine.media_processor.video_params.frame_brightness \
                    != self.media_engine.media_processor.video_params.get_day_mode_frame_brightness():
                self.media_engine.media_processor.set_frame_brightness_value(
                    self.media_engine.media_processor.video_params.get_day_mode_frame_brightness())
                self.hdmi_in_page.client_brightness_edit.setText(
                    str(self.media_engine.media_processor.video_params.get_frame_brightness()))
                self.medialist_page.client_brightness_edit.setText(
                    str(self.media_engine.media_processor.video_params.get_frame_brightness()))

                clients = self.clients
                for c in clients:
                    c.send_cmd(cmd_set_frame_brightness,
                               self.cmd_seq_id_increase(),
                               str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            if self.brightness_test_log is True:
                log.debug("self.media_engine.media_processor.video_params.frame_brightness = %d",
                      self.media_engine.media_processor.video_params.frame_brightness)

                data = self.city + " " + now.strftime("%Y-%m-%d %H:%M:%S")
                str_sunrise_time = sunrise_time.strftime("%Y-%m-%d %H:%M:%S")
                str_sunset_time = sunset_time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(data + "==> day mode" + "==>br:" +
                        str(self.media_engine.media_processor.video_params.get_frame_brightness()) +
                        "==>sunrisetime:" + str_sunrise_time +
                        "==>sunrisetime:" + str_sunset_time + "\n")
                f.flush()
        else:
            if self.brightness_test_log is True:
                log.debug("night mode")
            if self.media_engine.media_processor.video_params.frame_brightness \
                    != self.media_engine.media_processor.video_params.get_night_mode_frame_brightness():
                self.media_engine.media_processor.set_frame_brightness_value(
                    self.media_engine.media_processor.video_params.get_night_mode_frame_brightness())

                self.hdmi_in_page.client_brightness_edit.setText(
                    str(self.media_engine.media_processor.video_params.get_frame_brightness()))
                self.medialist_page.client_brightness_edit.setText(
                    str(self.media_engine.media_processor.video_params.get_frame_brightness()))

                clients = self.clients
                for c in clients:
                    c.send_cmd(cmd_set_frame_brightness,
                               self.cmd_seq_id_increase(),
                               str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            if self.brightness_test_log is True:
                log.debug("self.media_engine.media_processor.video_params.frame_brightness = %d",
                          self.media_engine.media_processor.video_params.get_frame_brightness())

                data = self.city + " " + now.strftime("%Y-%m-%d %H:%M:%S")
                str_sunrise_time = sunrise_time.strftime("%Y-%m-%d %H:%M:%S")
                str_sunset_time = sunset_time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(data + "==> night mode" + "==>br:" +
                        str(self.media_engine.media_processor.video_params.frame_brightness) +
                        "==>sunrisetime:" + str_sunrise_time +
                        "==>sunrisetime:" + str_sunset_time + "\n")
                f.flush()
        if self.brightness_test_log is True:
            f.close()

    def client_reboot_timer(self):
        if 'Disable' in self.reboot_mode:
            return
        # log.debug("client_reboot_timer")
        i_reboot_hour = int(self.reboot_time.split(":")[0])
        i_reboot_min = int(self.reboot_time.split(":")[1])
        # log.debug("client_reboot_timer : %d:%d", i_reboot_hour, i_reboot_min)
        now = datetime.now().replace(tzinfo=ZoneInfo(utils.astral_utils.get_time_zone(self.city)))
        start_client_reboot_time = now.replace(hour=i_reboot_hour, minute=i_reboot_min, second=0, microsecond=0)
        end_client_reboot_time = now.replace(hour=i_reboot_hour, minute=i_reboot_min + 1, second=0, microsecond=0)
        if start_client_reboot_time < now < end_client_reboot_time:
            log.debug("It's time to trigger reboot cmd!") 
            self.client_reboot_flags = True
            try:
                for i in range(10):
                    self.server_broadcast_client_reboot()
                    time.sleep(0.1)
            except Exception as e:
                log.debug(e)
            self.client_reboot_flags = False
            time.sleep(30)
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                os.popen("reboot")
            else:
                log.debug("SYSTEM fake reboot")

    def is_sleep_time(self, now, light_start_time, light_end_time):
        midnight_time = now.replace(hour=23, minute=59, second=59, microsecond=0)
        if light_end_time > light_start_time:
            if now < light_start_time or now > light_end_time:
                return True
            else:
                return False
        else:
            if light_end_time < now < light_start_time:
                return True
            else:
                return False
        return False

    def check_brightness_by_date_timer(self):
        if self.brightness_test_log is True:
            log.debug("frame_brightness_algorithm = %d",
                      self.media_engine.media_processor.video_params.frame_brightness_algorithm)

        if self.media_engine.media_processor.video_params.frame_brightness_algorithm \
                == frame_brightness_adjust.fix_mode:
            clients = self.clients
            for c in clients:
                c.send_cmd(cmd_set_frame_brightness,
                           self.cmd_seq_id_increase(),
                           str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            if self.brightness_test_log is True:
                log.debug("frame_brightness_adjust.fix_mode")
            return
        self.city = City_Map[self.media_engine.media_processor.video_params.get_target_city_index()].get("City")
        sunrise_time, sunset_time = utils.astral_utils.get_sun_times(self.city)
        # now = datetime.now().replace(tzinfo=(pytz.timezone(utils.astral_utils.get_time_zone(self.city))))
        # pytz have +08:06 ??!! the min is 06??? strange!!!
        now = datetime.now().replace(tzinfo=ZoneInfo(utils.astral_utils.get_time_zone(self.city)))
        # test_now = datetime.now(sunrise_time.tzinfo)
        # now = datetime.now(sunrise_time.tzinfo)
        # log.debug("now: %s", now.strftime("%Y-%m-%d %H:%M:%S"))
        # log.debug("test_now: %s", test_now.strftime("%Y-%m-%d %H:%M:%S"))
        # test_hour = now
        light_start_time = None
        light_end_time = None
        if utils.astral_utils.get_sleep_mode_enable() is True:
            # log.debug("Sleep Mode is True")
            # sleep start ==> train start
            light_start_time = now.replace(hour=self.i_sleep_end_time_hour, minute=self.i_sleep_end_time_min,
                                           second=0, microsecond=0)
            # sleep start ==> light_end
            light_end_time = now.replace(hour=self.i_sleep_start_time_hour, minute=self.i_sleep_start_time_min,
                                         second=0, microsecond=0)
        else:
            if self.brightness_test_log is True:
                log.debug("Sleep Mode is False")
            pass

        # now = test_hour.replace(hour=self.test_hour, minute=self.test_min, second=0, microsecond=0)

        # sunrise_time, sunset_time = utils.astral_utils.get_sun_times(self.city)
        if self.brightness_test_log is True:
            log.debug("sunrise_time: %s", sunrise_time)
            log.debug("sunset_time: %s", sunset_time)
        with open(os.getcwd() + "/static/sun_time.dat", "w+") as f:
            file_content = "sunrise_time:" + sunrise_time.strftime("%Y-%m-%d %H:%M:%S") + \
                           "\n" + "sunset_time:" + sunset_time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(file_content)
            f.close()
        # train info stop
        if light_start_time is not None and light_end_time is not None:
            # if now < light_start_time or now > light_end_time:
            if self.is_sleep_time(now, light_start_time, light_end_time) is True:
                if self.brightness_test_log is True:
                    file_uri = os.getcwd() + "/test_log.dat"
                    f = open(file_uri, "a+")
                    log.debug("sleep mode")
                if self.media_engine.media_processor.video_params.frame_brightness \
                        != self.media_engine.media_processor.video_params.get_sleep_mode_frame_brightness():
                    self.media_engine.media_processor.set_frame_brightness_value(
                        self.media_engine.media_processor.video_params.get_sleep_mode_frame_brightness())
                    self.hdmi_in_page.client_brightness_edit.setText(
                        str(self.media_engine.media_processor.video_params.get_frame_brightness()))
                    self.medialist_page.client_brightness_edit.setText(
                        str(self.media_engine.media_processor.video_params.get_frame_brightness()))

                    clients = self.clients
                    for c in clients:
                        c.send_cmd(cmd_set_frame_brightness,
                                   self.cmd_seq_id_increase(),
                                   str(self.media_engine.media_processor.video_params.get_frame_brightness()))
                if self.brightness_test_log is True:
                    log.debug("self.media_engine.media_processor.video_params.frame_brightness = %d",
                              self.media_engine.media_processor.video_params.frame_brightness)

                    data = self.city + " " + now.strftime("%Y-%m-%d %H:%M:%S")
                    str_sunrise_time = sunrise_time.strftime("%Y-%m-%d %H:%M:%S")
                    str_sunset_time = sunset_time.strftime("%Y-%m-%d %H:%M:%S")
                    f.write(data + "==> sleep mode" + "==>br:" +
                            str(self.media_engine.media_processor.video_params.frame_brightness) +
                            "==>sunrisetime:" + str_sunrise_time +
                            "==>sunrisetime:" + str_sunset_time + "\n")
                    f.flush()
                    f.close()
            else:
                self.check_daymode_nightmode(sunrise_time, sunset_time, now)
        else:
            self.check_daymode_nightmode(sunrise_time, sunset_time, now)

    def demo_start_cms(self):
        self.func_cms_setting()
        log.debug("demo_start play cms")
        self.cms_page.start_play_cms()

    def kill_ffmpy_process(self):
        log.debug("kill ffmpy process")

        try:
            log.debug("**************************************************************")
            os.kill(self.media_engine.media_processor.ffmpy_process.pid, signal.SIGTERM)
        except Exception as e:
            log.debug(e)

    def demo_start_hdmi_in(self):
        log.debug("timer trigger demo_start play_hdmi_in")
        self.func_hdmi_in_contents()
        log.debug("demo_start play_hdmi_in")
        self.hdmi_in_page.start_send_to_led()

    def demo_start_playlist(self):
        self.func_file_contents()
        log.debug("play playlist")
        self.media_engine.play_playlsit("TTDemo.playlist")

    # enter engineer mode
    def ctrl_e_trigger(self):
        log.debug(" ")
        self.engineer_mode = True
        self.init_ui()

    def closeEvent(self, event):
        log.debug("close")
        os.system("pkill ffmpeg")
        exit()

    def init_ui(self):
        self.setFixedSize(1280, 960)

        pagelayout = QGridLayout()
        """Left UI Start"""
        top_left_frame = QFrame(self)
        top_left_frame.setFrameShape(QFrame.StyledPanel)
        # 　lef layout vertical
        button_layout = QVBoxLayout(top_left_frame)
        top_left_frame.setMouseTracking(True)

        btm_left_frame = QFrame(self)
        btm_left_frame.setMouseTracking(True)

        version_label = QLabel(btm_left_frame)
        version_label.setMouseTracking(True)
        blank_layout = QVBoxLayout(btm_left_frame)

        version_label.setText("GIS LED\n" + "version:" + version)
        version_label.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        version_label.setFixedHeight(200)

        test_label = QLabel(btm_left_frame)
        test_pixmap = QPixmap("material/logo.jpg").scaledToWidth(200)

        test_label.setPixmap(test_pixmap)
        blank_layout.addWidget(test_label)

        blank_layout.addWidget(version_label)

        # btn for connect client
        connect_btn = QPushButton(top_left_frame)
        connect_btn.setMouseTracking(True)
        # connect_btn.setStyleSheet('QPushButton {background-color: #A3C1DA; color: orange;}')
        connect_btn.setFixedSize(self.option_btn_width, self.option_btn_height), connect_btn.setText(STR_CLIENT_INFO)
        connect_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        connect_btn.clicked.connect(self.fun_connect_clients)
        button_layout.addWidget(connect_btn)
        connect_btn.setMouseTracking(True)

        content_btn = QPushButton(top_left_frame)
        content_btn.setFixedSize(self.option_btn_width, self.option_btn_height), content_btn.setText(STR_MEDIA_CONTENT)
        content_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        content_btn.clicked.connect(self.func_file_contents)
        button_layout.addWidget(content_btn)

        hdmi_in_btn = QPushButton(top_left_frame)
        hdmi_in_btn.setFixedSize(self.option_btn_width, self.option_btn_height), hdmi_in_btn.setText(STR_HDMI_IN)
        hdmi_in_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        hdmi_in_btn.clicked.connect(self.func_hdmi_in_contents)
        button_layout.addWidget(hdmi_in_btn)

        test_btn = QPushButton(top_left_frame)
        test_btn.setFixedSize(self.option_btn_width, self.option_btn_height), test_btn.setText(STR_LED_SETTING)
        test_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        test_btn.clicked.connect(self.func_led_setting)
        button_layout.addWidget(test_btn)

        test2_btn = QPushButton(top_left_frame)
        test2_btn.setFixedSize(self.option_btn_width, self.option_btn_height), test2_btn.setText(STR_CMS)
        test2_btn.setFont(QFont(qfont_style_default, qfont_style_size_large))
        test2_btn.clicked.connect(self.func_cms_setting)
        button_layout.addWidget(test2_btn)
        """Left UI End"""

        """Right UI"""
        self.right_frame = QFrame(self)
        self.right_frame.setFrameShape(QFrame.StyledPanel)
        self.right_frame.setMouseTracking(True)
        # 右边显示为stack布局
        self.right_layout = QStackedLayout(self.right_frame)

        """QTableWidget"""
        self.initial_client_table_page()

        """QTreeWidgetFile Tree in Tab.2"""
        self.initial_media_file_page()

        """Qt Hdmi-in Page in Tab.3"""
        self.initial_hdmi_in_page()

        """QTreeWidget for LED Setting"""
        self.initial_led_layout_page()

        "CMS Page"
        self.initial_cms_page()

        self.splitter1 = QSplitter(Qt.Vertical)
        self.splitter1.setMouseTracking(True)
        top_left_frame.setFixedHeight(360)
        top_left_frame.setFixedWidth(260)
        self.splitter1.addWidget(top_left_frame)
        self.splitter1.addWidget(btm_left_frame)

        self.splitter2 = QSplitter(Qt.Horizontal)
        self.splitter2.addWidget(self.splitter1)
        self.splitter2.setMouseTracking(True)
        # 　add right layout frame
        self.right_frame.setMouseTracking(True)
        self.splitter2.addWidget(self.right_frame)
        self.splitter2.setMouseTracking(True)
        # 窗口部件添加布局
        widget = QWidget()
        pagelayout.addWidget(self.splitter2)
        widget.setLayout(pagelayout)
        widget.setMouseTracking(True)
        self.setCentralWidget(widget)

        media_preview_widget = QLabel()
        media_preview_widget.setFrameShape(QFrame.StyledPanel)
        media_preview_widget.setWindowFlags(Qt.ToolTip)
        media_preview_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        media_preview_widget.hide()
        self.media_preview_widget = media_preview_widget

    def initial_client_table_page(self):
        self.client_page = clients_page(self, self.clients)

    def initial_media_file_page(self):
        self.medialist_page = media_page(self)

    def initial_hdmi_in_page(self):
        self.hdmi_in_page = Hdmi_In_Page(self)

    def initial_led_layout_page(self):
        self.led_setting = QWidget(self.right_frame)

        ''' led setting options'''
        ''' led resolution setting'''
        self.led_setting_width_textlabel = QLabel(self.right_frame)
        self.led_setting_width_textlabel.setText('LED Wall Width:')
        self.led_setting_width_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_setting_width_editbox = QLineEdit(self.right_frame)
        self.led_setting_width_editbox.setFixedWidth(100)
        self.led_setting_width_editbox.setText(str(self.led_wall_width))
        self.led_setting_height_textlabel = QLabel(self.right_frame)
        self.led_setting_height_textlabel.setText('LED Wall Height:')
        self.led_setting_height_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_setting_height_editbox = QLineEdit(self.right_frame)
        self.led_setting_height_editbox.setFixedWidth(100)
        self.led_setting_height_editbox.setText(str(self.led_wall_height))
        self.led_res_check_btn = QPushButton()
        self.led_res_check_btn.clicked.connect(self.set_led_wall_size)
        self.led_res_check_btn.setText("Confirm")
        self.led_res_check_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))



        # led brightness setting
        self.led_brightness_textlabel = QLabel(self.right_frame)
        self.led_brightness_textlabel.setText('LED Brightness:')
        self.led_brightness_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_brightness_editbox = QLineEdit(self.right_frame)
        self.led_brightness_editbox.setFixedWidth(100)
        self.led_brightness_editbox.setText(str(self.led_wall_brightness))

        # led contrast setting
        self.led_contrast_textlabel = QLabel(self.right_frame)
        self.led_contrast_textlabel.setText('LED Contrast:')
        self.led_contrast_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_contrast_editbox = QLineEdit(self.right_frame)
        self.led_contrast_editbox.setFixedWidth(100)
        self.led_contrast_editbox.setText(str(self.led_wall_brightness))

        # rgb gain
        self.led_redgain_textlabel = QLabel(self.right_frame)
        self.led_redgain_textlabel.setText('Red Gain:')
        self.led_redgain_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_redgain_editbox = QLineEdit(self.right_frame)
        self.led_redgain_editbox.setFixedWidth(80)
        self.led_redgain_editbox.setText(str(self.led_wall_brightness))

        self.led_greengain_textlabel = QLabel(self.right_frame)
        self.led_greengain_textlabel.setText('Red Gain:')
        self.led_greengain_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_greengain_editbox = QLineEdit(self.right_frame)
        self.led_greengain_editbox.setFixedWidth(80)
        self.led_greengain_editbox.setText(str(self.led_wall_brightness))

        self.led_bluegain_textlabel = QLabel(self.right_frame)
        self.led_bluegain_textlabel.setText('Red Gain:')
        self.led_bluegain_textlabel.setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_bluegain_editbox = QLineEdit(self.right_frame)
        self.led_bluegain_editbox.setFixedWidth(80)
        self.led_bluegain_editbox.setText(str(self.led_wall_brightness))

        self.led_brightness_check_btn = QPushButton()
        self.led_brightness_check_btn.clicked.connect(self.set_led_wall_brightness)
        self.led_brightness_check_btn.setText("Confirm")
        self.led_brightness_check_btn.setFont(QFont(qfont_style_default, qfont_style_size_medium))

        self.led_setting_layout = QGridLayout()

        self.led_setting_layout.addWidget(self.led_setting_width_textlabel, 0, 1)
        self.led_setting_layout.addWidget(self.led_setting_width_editbox, 0, 2)
        self.led_setting_layout.addWidget(self.led_setting_height_textlabel, 0, 3)
        self.led_setting_layout.addWidget(self.led_setting_height_editbox, 0, 4)
        self.led_setting_layout.addWidget(self.led_res_check_btn, 0, 7)

        self.led_setting_layout.addWidget(self.led_brightness_textlabel, 1, 1)
        self.led_setting_layout.addWidget(self.led_brightness_editbox, 1, 2)
        self.led_setting_layout.addWidget(self.led_contrast_textlabel, 1, 3)
        self.led_setting_layout.addWidget(self.led_contrast_editbox, 1, 4)

        self.led_setting_layout.addWidget(self.led_redgain_textlabel, 2, 1)
        self.led_setting_layout.addWidget(self.led_redgain_editbox, 2, 2)
        self.led_setting_layout.addWidget(self.led_greengain_textlabel, 2, 3)
        self.led_setting_layout.addWidget(self.led_greengain_editbox, 2, 4)
        self.led_setting_layout.addWidget(self.led_bluegain_textlabel, 2, 5)
        self.led_setting_layout.addWidget(self.led_bluegain_editbox, 2, 6)

        self.led_setting_layout.addWidget(self.led_brightness_check_btn, 2, 7)

        self.led_setting.setLayout(self.led_setting_layout)

        # self.led_setting_layout.addWidget(self.led_fake_label, 1, 0, 1, 5)
        self.led_client_layout_tree = CTreeWidget(self.right_frame)
        # self.led_client_layout_tree.mouseMove.connect(self.led_client_layout_mouse_move)
        self.led_client_layout_tree.setMouseTracking(True)
        self.led_client_layout_tree.setSelectionMode(QAbstractItemView.MultiSelection)

        self.led_client_layout_tree.doubleClicked.connect(self.cabinet_setting_window_show)

        self.led_client_layout_tree.setColumnCount(1)
        self.led_client_layout_tree.setColumnWidth(0, 300)
        self.led_client_layout_tree.header().setFont(QFont(qfont_style_default, qfont_style_size_medium))
        self.led_client_layout_tree.headerItem().setText(0, "Client Layout")


        font = QFont()
        font.setPointSize(24)
        self.led_client_layout_tree.setFont(font)

        self.led_setting_layout.addWidget(self.led_client_layout_tree, 3, 0, 1, 8)

        self.led_setting_layout.setRowStretch(2, 1)
        self.right_layout.addWidget(self.led_setting)

        port_layout_information_widget = QLabel()
        port_layout_information_widget.setFrameShape(QFrame.StyledPanel)
        port_layout_information_widget.setWindowFlags(Qt.ToolTip)
        port_layout_information_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        port_layout_information_widget.hide()
        self.port_layout_information_widget = port_layout_information_widget

    def initial_cms_page(self):
        """self.cms_widget = QWidget(self.right_frame)
        self.right_layout.addWidget(self.cms_widget)
        self.cms_widget_layout = QGridLayout()
        self.btn_test_cms = QPushButton(self.cms_widget)
        self.cms_widget_layout.addWidget(self.btn_test_cms,0, 1)
        self.cms_widget.setLayout(self.cms_widget_layout)"""

        self.cms_page = CmsPage(self)

    def center(self):
        # get the geomertry of the screen and set the postion in the center of screen

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

    def play_status_changed(self, changed, status):
        # log.debug("changed = %d", changed)
        # log.debug("status = %d", status)
        d0_str = ""
        d1_str = ""
        input_source = ""
        if status == play_status.stop:
            d0_str = "STANDBY"
        elif status == play_status.pausing:
            d0_str = "PAUSE"
        elif status == play_status.playing:
            d0_str = "PLAYING"
        if self.media_engine.media_processor.ffmpy_process is not None:
            # log.debug("process name : %d", self.media_engine.media_processor.ffmpy_process.pid)
            # log.debug("process name : %s", self.media_engine.media_processor.ffmpy_process.args)
            if "v4l2" in self.media_engine.media_processor.ffmpy_process.args:
                d1_str = "HDMI-In Source"
            else:
                d1_str = "FILE Source"

        # log.debug("d0_str = %s", d0_str)
        # log.debug("d1_str = %s", d1_str)
        self.lcd1602.add_data("LCD_TAG_PLAY_STATUS_INFO", d0_str, d1_str)

    def right_page_change_index(self, pre_idx, going_idx):
        '''if pre_idx == going_idx:
            return'''
        self.page_ui_mutex.lock()
        log.debug("")
        # handle page_hdmi_in_content enter and exit
        if pre_idx != page_hdmi_in_content_idx and going_idx == page_hdmi_in_content_idx:
            log.debug("start hdmi-in preview")
            self.media_engine.resume_play()
            self.media_engine.stop_play()
            self.hdmi_in_page.start_hdmi_in_preview()
        if pre_idx == page_hdmi_in_content_idx and going_idx != page_hdmi_in_content_idx:
            log.debug("stop hdmi-in preview")
            self.hdmi_in_page.stop_send_to_led()
            self.hdmi_in_page.stop_hdmi_in_preview()

        # handle page_cms_setting_idx enter and exit
        #if pre_idx != page_cms_setting_idx and going_idx == page_cms_setting_idx:
            '''try:
                self.media_engine.stop_play()
                self.cms_page.start_play_cms()
            except Exception as e:
                log.debug(e)'''
            
        if pre_idx == page_cms_setting_idx and going_idx != page_cms_setting_idx:
            try:
                self.cms_page.stop_play_cms()
                self.media_engine.resume_play()
                self.media_engine.stop_play()
                subprocess.Popen("pkill chromium", shell=True)
            except Exception as e:
                log.debug(e)

        log.debug("change page")

        self.pre_page_idx = self.page_idx
        self.page_idx = going_idx
        log.debug("self.page_idx = %d", self.page_idx)
        self.right_layout.setCurrentIndex(self.page_idx)
        self.page_ui_mutex.unlock()

        log.debug("change page ok!")
        # for test
        '''if going_idx == page_cms_setting_idx:
            self.media_engine.stop_play()
            self.cms_page.start_play_cms()
        else :
            self.cms_page.stop_play_cms()
            self.media_engine.resume_play()
            self.media_engine.stop_play()
            subprocess.Popen("pkill chromium", shell=True)'''

    def fun_connect_clients(self):
        log.debug("connect clients")
        # self.page_idx = 0
        # self.right_layout.setCurrentIndex(self.page_idx)
        self.signal_right_page_changed.emit(self.page_idx, page_client_connect_idx)
        self.page_status_change()

    def func_file_contents(self):
        log.debug("file contents")
        # self.page_idx = 1
        # self.right_layout.setCurrentIndex(self.page_idx)
        self.signal_right_page_changed.emit(self.page_idx, page_media_content_idx)
        self.page_status_change()

    def func_hdmi_in_contents(self):
        log.debug("hdmi-in contents")
        # self.page_idx = 2
        # self.right_layout.setCurrentIndex(self.page_idx)
        self.signal_right_page_changed.emit(self.page_idx, page_hdmi_in_content_idx)
        self.page_status_change()

    def func_led_setting(self):
        log.debug("func_led_setting")
        # self.page_idx = 3
        # self.right_layout.setCurrentIndex(self.page_idx)
        self.signal_right_page_changed.emit(self.page_idx, page_led_setting_idx)
        self.page_status_change()
        self.led_layout_window.show()

    def func_cms_setting(self):
        log.debug("func_cms_setting")
        self.signal_right_page_changed.emit(self.page_idx, page_cms_setting_idx)
        self.page_status_change()

    def func_cmd_setting(self):
        log.debug("func_cmd_setting")
        self.signal_right_page_changed.emit(self.page_idx, page_cmd_setting_idx)
        self.page_status_change()

    def test_brightness_loop(self):
        i = int(self.medialist_page.client_brightness_edit.text())
        i += 1
        if i > 255 :
            i = 0
        utils.ffmpy_utils.ffmpy_draw_text(str(i))
        self.medialist_page.client_brightness_edit.setText(str(i))
        self.medialist_page.video_params_confirm_btn_clicked()

    """ handle the command from qlocalserver"""
    def parser_cmd_from_qlocalserver(self, data):
        if data.get("play_file"):
            now_time = time.time()
            if now_time - self.web_cmd_time < web_cmd_interval:
                log.debug("cmd too quick")
                return
            self.web_cmd_time = time.time()
            got_lock = self.web_cmd_mutex.tryLock()
            if got_lock is False:
                log.debug("Cannot get lock!")
                return
            else:
                pass
            try:
                self.func_file_contents()
                log.debug("play single file : %s!", data.get("play_file"))
                self.medialist_page.right_clicked_select_file_uri = \
                    internal_media_folder + "/" + data.get("play_file")
                log.debug("file_uri :%s",
                          self.medialist_page.right_clicked_select_file_uri)
                self.media_engine.play_single_file(
                    self.medialist_page.right_clicked_select_file_uri)
            except Exception as e:
                log.debug(e)
            self.web_cmd_mutex.unlock()
        elif data.get("play_cms"):
            now_time = time.time()
            if now_time - self.web_cmd_time < web_cmd_interval:
                log.debug("cmd too quick")
                return
            self.web_cmd_time = time.time()
            got_lock = self.web_cmd_mutex.tryLock()
            if got_lock is False:
                log.debug("Cannot get lock!")
                return
            else:
                pass
            try:
                log.debug("got play_cms ")
                self.func_cms_setting()
                self.cms_page.start_play_cms()
            except Exception as e:
                log.debug(e)
            self.web_cmd_mutex.unlock()
        elif data.get("play_playlist"):
            now_time = time.time()
            if now_time - self.web_cmd_time < web_cmd_interval:
                log.debug("cmd too quick")
                return
            self.web_cmd_time = time.time()
            got_lock = self.web_cmd_mutex.tryLock()
            if got_lock is False:
                log.debug("Cannot get lock!")
                return
            else:
                pass
            try:
                self.func_file_contents()
                log.debug("play playlist")
                self.media_engine.play_playlsit(data.get("play_playlist"))
            except Exception as e:
                log.debug(e)
            self.web_cmd_mutex.unlock()
        elif data.get("play_hdmi_in"):
            now_time = time.time()
            if now_time - self.web_cmd_time < web_cmd_interval:
                log.debug("cmd too quick")
                return
            self.web_cmd_time = time.time()
            got_lock = self.web_cmd_mutex.tryLock()
            if got_lock is False:
                log.debug("Cannot get lock!")
                return
            else:
                pass
            try:
                self.func_hdmi_in_contents()
                if "start" in data.get("play_hdmi_in"):
                    log.debug("play_hdmi_in start")
                    # self.hdmi_in_page.play_action_btn.click()
                    self.hdmi_in_page.send_to_led_parser()
                elif "stop" in data.get("play_hdmi_in"):
                    log.debug("play_hdmi_in stop")
                    self.hdmi_in_page.stop_send_to_led()
            except Exception as e:
                log.debug(e)
            self.web_cmd_mutex.unlock()
        elif data.get("play_text"):
            now_time = time.time()
            if now_time - self.web_cmd_time < web_cmd_interval:
                log.debug("cmd too quick")
                return
            self.web_cmd_time = time.time()
            got_lock = self.web_cmd_mutex.tryLock()
            if got_lock is False:
                log.debug("Cannot get lock!")
                return
            else:
                pass
            try:
                self.func_file_contents()
                log.debug("play_text")
                utils.file_utils.change_text_content(data.get("play_text"))
                self.medialist_page.right_clicked_select_file_uri = internal_media_folder + subtitle_blank_jpg
                log.debug("file_uri :%s", self.medialist_page.right_clicked_select_file_uri)
                self.media_engine.play_single_file(self.medialist_page.right_clicked_select_file_uri)
            except Exception as e:
                log.debug(e)
            self.web_cmd_mutex.unlock()
        elif data.get("set_text_size"):
            log.debug("set_text_size")
            utils.file_utils.change_text_size(data.get("set_text_size"))
        elif data.get("set_text_speed"):
            log.debug("set_text_speed")
            utils.file_utils.change_text_speed(data.get("set_text_speed"))
        elif data.get("set_text_position"):
            log.debug("set_text_position")
            utils.file_utils.change_text_position(data.get("set_text_position"))
        elif data.get("set_text_period"):
            log.debug("set_text_period")
            utils.file_utils.change_text_period(data.get("set_text_period"))
        elif data.get("set_repeat_option"):
            log.debug("set_repeat_option")
            if data.get("set_repeat_option") == "Repeat_Random":
                self.medialist_page.play_option_repeat = repeat_option.repeat_random
                self.medialist_page.btn_repeat.setText("Repeat Random")
            elif data.get("set_repeat_option") == "Repeat_All":
                self.medialist_page.play_option_repeat = repeat_option.repeat_all
                self.medialist_page.btn_repeat.setText("Repeat All")
            elif data.get("set_repeat_option") == "Repeat_One":
                self.medialist_page.play_option_repeat = repeat_option.repeat_one
                self.medialist_page.btn_repeat.setText("Repeat One")
            elif data.get("set_repeat_option") == "Repeat_None":
                self.medialist_page.play_option_repeat = repeat_option.repeat_none
                self.medialist_page.btn_repeat.setText("Repeat None")
            self.mainwindow.repeat_option_set(self.medialist_page.play_option_repeat)
        elif data.get("set_frame_brightness_option"):
            log.debug("set_frame_brightness_option")
            self.media_engine.media_processor.set_frame_brightness_value(int(data.get("set_frame_brightness_option")))
            # print("type(self.media_engine.media_processor.video_params.get_frame_brightness()):", self.media_engine.media_processor.video_params.get_frame_brightness())
            self.hdmi_in_page.client_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            self.medialist_page.client_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_frame_brightness()))

            clients = self.clients
            for c in clients:
                c.send_cmd(cmd_set_frame_brightness,
                           self.cmd_seq_id_increase(),
                           str(self.media_engine.media_processor.video_params.frame_brightness))
        elif data.get("set_sleep_mode"):
            log.debug("recv : %s ", data.get("set_sleep_mode"))
            if data.get("set_sleep_mode") == "Enable":
                log.debug("sleep_mode_set_enable")
                self.media_engine.media_processor.set_sleep_mode(1)
                log.debug("sleep_mode_set_enableA")
                self.medialist_page.radiobutton_sleep_mode_enable_set()
                log.debug("sleep_mode_set_enableB")
                self.hdmi_in_page.radiobutton_sleep_mode_enable_set()
                log.debug("sleep_mode_set_enableC")
            else:
                log.debug("sleep_mode_set_disable")
                self.media_engine.media_processor.set_sleep_mode(0)
                self.medialist_page.radiobutton_sleep_mode_disable_set()
                self.hdmi_in_page.radiobutton_sleep_mode_disable_set()
        elif data.get("set_reboot_mode"):
            log.debug("set_reboot_mode")
            reboot_time = utils.file_utils.get_reboot_time_default_from_file()
            if data.get("set_reboot_mode") == "Enable":
                log.debug("set_reboot_mode : Enable")
                utils.file_utils.set_reboot_params(True, reboot_time)
            else:
                log.debug("set_reboot_mode : Disable")
                utils.file_utils.set_reboot_params(False, reboot_time)
            self.reboot_mode = utils.file_utils.get_reboot_mode_default_from_file()
            self.reboot_time = utils.file_utils.get_reboot_time_default_from_file()
        elif data.get("set_reboot_time"):
            log.debug("set_reboot_time: %s", data.get("set_reboot_time"))
            reboot_mode = utils.file_utils.get_reboot_mode_default_from_file()
            if reboot_mode is "Enable":
                utils.file_utils.set_reboot_params(True, data.get("set_reboot_time"))
            else:
                utils.file_utils.set_reboot_params(False, data.get("set_reboot_time"))
            self.reboot_time = utils.file_utils.get_reboot_time_default_from_file()
            self.reboot_mode = utils.file_utils.get_reboot_mode_default_from_file()
        elif data.get("set_sleep_time"):
            log.debug("set_sleep_time: %s", data.get("set_sleep_time"))
            time_tmp = data.get("set_sleep_time")
            self.sleep_start_time = time_tmp.split(";")[0]
            self.sleep_end_time = time_tmp.split(";")[1]
            utils.file_utils.set_sleep_params(self.sleep_start_time, self.sleep_end_time)
            self.i_sleep_start_time_hour = int(self.sleep_start_time.split(":")[0])
            self.i_sleep_start_time_min = int(self.sleep_start_time.split(":")[1])
            self.i_sleep_end_time_hour = int(self.sleep_end_time.split(":")[0])
            self.i_sleep_end_time_min = int(self.sleep_end_time.split(":")[1])

        elif data.get("set_target_city"):
            log.debug("recv : %s ", data.get("set_target_city"))
            if utils.astral_utils.check_city_valid(data.get("set_target_city")) is False:
                log.debug("City Invalid")
                return
            # self.city = data.get("set_target_city")
            c = 0
            city_index = 0
            for city in City_Map:
                if city.get("City") == data.get("set_target_city"):
                    city_index = c
                    break
                c += 1
            self.medialist_page.combobox_target_city_change(city_index)
            self.city = City_Map[self.media_engine.media_processor.video_params.get_target_city_index()].get("City")

        elif data.get("set_brightness_algo"):
            log.debug("recv : %s ", data.get("set_brightness_algo"))
            if "fix_mode" == data.get("set_brightness_algo"):
                self.medialist_page.radiobutton_client_br_method_fix_mode_set()
                self.hdmi_in_page.radiobutton_client_br_method_fix_mode_set()
            elif "auto_time_mode" == data.get("set_brightness_algo"):
                self.medialist_page.radiobutton_client_br_method_time_mode_set()
                self.hdmi_in_page.radiobutton_client_br_method_time_mode_set()
            elif "auto_als_mode" == data.get("set_brightness_algo"):
                self.medialist_page.radiobutton_client_br_method_als_mode_set()
                self.hdmi_in_page.radiobutton_client_br_method_als_mode_set()
            elif "test_mode" == data.get("set_brightness_algo"):
                self.medialist_page.radiobutton_client_br_method_test_mode_set()
                self.hdmi_in_page.radiobutton_client_br_method_test_mode_set()
        elif data.get("set_frame_brightness_values_option"):
            log.debug("recv : %s", data.get("set_frame_brightness_values_option"))
            data_tmp = data.get("set_frame_brightness_values_option")
            fr_br = data_tmp.split(";")[0].split(":")[1]
            day_mode_fr_br = data_tmp.split(";")[1].split(":")[1]
            night_mode_fr_br = data_tmp.split(";")[2].split(":")[1]
            sleep_mode_fr_br = data_tmp.split(";")[3].split(":")[1]
            log.debug("fr_br : %s", fr_br)
            log.debug("day_mode_fr_br : %s", day_mode_fr_br)
            log.debug("night_mode_fr_br : %s", night_mode_fr_br)
            log.debug("sleep_mode_fr_br : %s", sleep_mode_fr_br)
            self.media_engine.media_processor.set_frame_brightness_value(int(fr_br))
            self.media_engine.media_processor.set_day_mode_frame_brightness_value(int(day_mode_fr_br))
            self.media_engine.media_processor.set_night_mode_frame_brightness_value(int(night_mode_fr_br))
            self.media_engine.media_processor.set_sleep_mode_frame_brightness_value(int(sleep_mode_fr_br))
            self.hdmi_in_page.client_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            self.medialist_page.client_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_frame_brightness()))
            self.hdmi_in_page.client_day_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_day_mode_frame_brightness()))
            self.medialist_page.client_day_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_day_mode_frame_brightness()))
            self.hdmi_in_page.client_night_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_night_mode_frame_brightness()))
            self.medialist_page.client_night_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_night_mode_frame_brightness()))
            self.hdmi_in_page.client_sleep_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_sleep_mode_frame_brightness()))
            self.medialist_page.client_sleep_mode_brightness_edit.setText(
                str(self.media_engine.media_processor.video_params.get_sleep_mode_frame_brightness()))

            self.check_brightness_by_date_timer()

        elif data.get("set_ledclients_reboot_option"):
            log.debug("set_ledclients_reboot_option")
            # clients = self.clients
            
            self.client_reboot_flags = True
            try:
                for i in range(10):
                    self.server_broadcast_client_reboot()
                    time.sleep(0.1)
            except Exception as e:
                log.debug(e)
            self.client_reboot_flags = False
            '''for c in clients:
                reboot_cmd = "sshpass -p workout13 ssh -o StrictHostKeyChecking=no root@" + c.client_ip + " " + "reboot"
                log.debug("reboot_cmd : %s", reboot_cmd)
                k = os.popen(reboot_cmd)
                k.close()'''


        elif data.get("start_color_test"):
            log.debug("start_color_test")
            clients = self.clients
            for c in clients:
                c.send_cmd(cmd_set_test_color,
                           self.cmd_seq_id_increase(),
                           str(data.get("start_color_test")))
        elif data.get("stop_color_test"):
            log.debug("stop_color_test")
            clients = self.clients
            for c in clients:
                c.send_cmd(cmd_set_test_color,
                           self.cmd_seq_id_increase(),
                           str(data.get("stop_color_test")))

    def check_client(self, ip, data):
        is_found = False
        tmp_client = None
        c_version = ""
        try:
            self.clients_lock()
            c_version = data.split(";")[1].split(":")[1]
            if "fps" in data:
                c_fps = data.split(",")[1].split(":")[1]
            # log.debug("c_fps = %d", int(c_fps))
            # self.clients_lock()
            for c in self.clients:
                # log.debug("client ip :%s ", c.client_ip)
                if c.client_ip == ip:
                    is_found = True
                    ###
                    if "fps" in data:
                        if int(c_fps) == 0:
                            c.fps_zero_count += 1
                            if c.fps_zero_count >= 10:
                                log.debug("+++++++++++kill ffmpy process timer launch!+++++++++++")
                                QTimer.singleShot(2000, self.kill_ffmpy_process)
                                c.fps_zero_count = 0
                                log.debug("client ip %s zero fps counts >= 10", c.client_ip)
                        else:
                            c.fps_zero_count = 0
                    ###
                    tmp_client = c
                    break
            """ no such client ip in clients list, new one and append"""
            if is_found is False:
                log.debug("client_id_count = %d", self.client_id_count)
                c = client(ip, net_utils.get_ip_address(), c_version, self.client_id_count)
                # connect signal/slot function
                c.signal_send_cmd_ret.connect(self.client_send_cmd_ret)
                c.signal_cabinet_params_changed.connect(self.send_cmd_set_cabinet_params)
                c.signal_sync_cabinet_params.connect(self.sync_cabinet_params)

                self.client_id_count += 1
                self.clients.append(c)

                # add clients in web page
                set_tmp_clients(self.clients)
                # send brightness and br_divisor to the new client
                c.send_cmd(cmd_set_frame_brightness,
                           self.cmd_seq_id_increase(),
                           str(self.media_engine.media_processor.video_params.frame_brightness))

                c.send_cmd(cmd_set_frame_br_divisor,
                           self.cmd_seq_id_increase(),
                           str(self.media_engine.media_processor.video_params.frame_br_divisor))

                c.send_cmd(cmd_set_frame_gamma,
                           self.cmd_seq_id_increase(),
                           str(self.media_engine.media_processor.video_params.frame_gamma))

                c.send_cmd(cmd_set_client_id,
                           self.cmd_seq_id_increase(),
                           str(c.client_id))

                self.sync_client_cabinet_params(c.client_ip, False)
                self.client_page.refresh_clients(self.clients)
                self.client_page.refresh_client_table()

                try:
                    with open(os.getcwd() + "/static/client_info.dat", "w+") as client_file:
                        for c in self.clients:
                            log.debug("write client info ip : %s", c.client_ip)
                            client_file.write("ip:" + c.client_ip + ";id:" + str(c.client_id) + "\n")
                    client_file.close()
                except Exception as e:
                    log.debug(e)


            else:
                """ find this ip in clients list, set the alive report count"""
                tmp_client.set_alive_count(3)
        except Exception as e:
            log.debug(e)
        finally:
            self.clients_unlock()




    def sync_cabinet_params(self, cab_params):
        ''' change led setting page treewidget'''
        # log.debug("")
        finditems = self.led_client_layout_tree.findItems(cab_params.client_ip, Qt.MatchContains, 1)
        for item in finditems:
            log.debug("%s", item.text(0))
        # for i in range(self.led_client_layout_tree.size()):
        #    log.debug("%d : %s", i, self.led_client_layout_tree.itemFromIndex(i).text(0))

    """send broadcast on eth0"""
    def server_broadcast_client_reboot(self):
        
        data=server_broadcast_message
        port=server_broadcast_port

        data_append = ";br:" + str(self.media_engine.media_processor.video_params.frame_brightness)
        data += data_append

        if self.client_reboot_flags is True:
            reboot_cmd_append = ";reboot"
            data += reboot_cmd_append

        ip = net_utils.get_ip_address()
        utils.net_utils.force_set_eth_ip()

        msg = data.encode()
        if ip != "":
            # print(f'sending on {ip}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((ip, 0))
            sock.sendto(msg, ("255.255.255.255", port))
            sock.close()

    
    """send broadcast on eth0"""
    def server_broadcast(self, arg):
        data = arg.get("data")
        port = arg.get("port")

        data_append = ";br:" + str(self.media_engine.media_processor.video_params.frame_brightness)
        data += data_append

        ip = net_utils.get_ip_address()
        utils.net_utils.force_set_eth_ip()

        msg = data.encode()
        if ip != "":
            # print(f'sending on {ip}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            sock.bind((ip, 0))
            sock.sendto(msg, ("255.255.255.255", port))
            sock.close()

        sleep(2)

    def clients_lock(self):
        self.clients_mutex.lock()

    def clients_unlock(self):
        self.clients_mutex.unlock()

    def refresh_clients_list(self, arg):
        # is_list_changed = False
        ori_len = len(self.clients)
        try:
            self.clients_lock()
            ori_len = len(self.clients)
            sleep_time = arg.get("sleep_time")
            for c in self.clients:
                c.decrese_alive_count()
                if c.get_alive_count() <= 0:
                    self.clients.remove(c)

            """for c in self.clients:
                log.debug("c.client_ip : %s ", c.client_ip)"""
        except Exception as e:
            log.debug(e)
        finally:
            if ori_len != len(self.clients):
                self.client_page.refresh_clients(self.clients)
                self.client_page.refresh_client_table()
                # self.refresh_client_table()
            self.clients_unlock()
        # test @1006 night
        #if self.tmp_clients_count != len(self.clients):
        #    self.tmp_clients_count = len(self.clients)
        #    QTimer.singleShot(2000, self.kill_ffmpy_process)

        sleep(sleep_time)
        self.sync_client_layout_params(False, True, False)

    def sync_client_layout_params(self, force_refresh, fresh_layout_map, remove_all_cabinet_label):
        # led layout page tree widget show
        if self.led_client_layout_tree.topLevelItemCount() != len(self.clients):
            force_refresh = True
            self.led_layout_window.remove_all_cabinet_label()

        # if remove_all_cabinet_label is True:
        #    self.led_layout_window.remove_all_cabinet_label()

        if force_refresh is True:
            self.client_led_layout.clear()
            self.led_client_layout_tree.clear()

            for c in self.clients:
                client_led_layout = QTreeWidgetItem(self.led_client_layout_tree)
                client_led_layout.setText(0, "id:" + str(c.client_id) + "(ip:" + c.client_ip + ")")
                for i in range(8):
                    port_layout = QTreeWidgetItem(client_led_layout)
                    port_layout.setText(0, "port" + str(i) + ":")

                    '''cabinet params test start '''
                    test_params = QTreeWidgetItem(port_layout)
                    test_params.setText(0, 'cabinet_width:' + str(c.cabinets_setting[i].cabinet_width))
                    test_params = QTreeWidgetItem(port_layout)
                    test_params.setText(0, 'cabinet_height:' + str(c.cabinets_setting[i].cabinet_height))
                    test_params = QTreeWidgetItem(port_layout)
                    test_params.setText(0, 'start_x:' + str(c.cabinets_setting[i].start_x))
                    test_params = QTreeWidgetItem(port_layout)
                    test_params.setText(0, 'start_y:' + str(c.cabinets_setting[i].start_y))
                    test_params = QTreeWidgetItem(port_layout)

                    test_pixmap = utils.qtui_utils.gen_led_layout_type_pixmap(96, 96, 10,
                                                                              c.cabinets_setting[i].layout_type)
                    qicon_type = QIcon(test_pixmap)
                    test_params.setIcon(0, qicon_type)
                    '''cabinet params test end '''
                    # gen cabinet label in led_wall_layout_window
                    if fresh_layout_map is True:
                        self.signal_add_cabinet_label.emit(c.cabinets_setting[i])
                ''' set icon size'''
                self.led_client_layout_tree.setIconSize(QSize(64, 64))
                if fresh_layout_map is True:
                    self.client_led_layout.append(client_led_layout)

    @pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onFileTreeItemClicked(self, it, col):
        log.debug("%s, %s, %s", it, col, it.text(col))
        file_uri = ""
        if it.parent() is not None:
            log.debug("%s", it.parent().text(0))
            # play the file
            if it.parent().text(0) == 'Internal Media':
                file_uri = internal_media_folder + "/" + it.text(col)
            else:
                if 'External Media' in it.parent().text(0):
                    dir = it.parent().text(0).split(":")[1]
                    file_uri = dir + "/" + it.text(col)

            log.debug("%s", file_uri)

    '''client table right clicked slot function'''
    def clientsmenucontexttree(self, position):
        q_table_widget_item = self.client_page.client_table.itemAt(position)
        if q_table_widget_item is None:
            return
        log.debug("client ip :%s", q_table_widget_item.text())
        self.right_click_select_client_ip = q_table_widget_item.text()

        pop_menu = QMenu()
        set_qstyle_dark(pop_menu)

        fw_upgrade_act = QAction("fw upgrade", self)
        pop_menu.addAction(fw_upgrade_act)
        pop_menu.addSeparator()
        test_act = QAction("test", self)
        pop_menu.addAction(test_act)
        pop_menu.triggered[QAction].connect(self.pop_menu_trigger_act)

        pop_menu.exec_(self.client_page.client_table.mapToGlobal(position))

    # All pop menu trigger act
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
                # launch a dialog
                # pop up a playlist generation dialog
                if self.NewPlaylistDialog is None:
                    self.NewPlaylistDialog = NewPlaylistDialog(self.media_engine.playlist)
                self.NewPlaylistDialog.signal_new_playlist_generate.connect(self.slot_new_playlist)
                self.NewPlaylistDialog.show()
            else:
                self.media_engine.add_to_playlist(playlist_name, self.right_clicked_select_file_uri)

        elif q.text() == "fw upgrade":
            log.debug("fw upgrade")
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                upgrade_file_uri = QFileDialog.getOpenFileName(None, "Select Upgrade File", "/home/root/")
            else:
                upgrade_file_uri = QFileDialog.getOpenFileName(None, "Select Upgrade File", "/home/venom/",
                                                               "SWU File (*.swu)")

            if upgrade_file_uri == "":
                log.debug("No select")
                return
            log.debug("upgrade_file_uri = %s", upgrade_file_uri[0])
            if upgrade_file_uri[0].endswith("swu"):
                log.debug("Goto upgrade!")
                ips = []
                ips.append(self.right_click_select_client_ip)
                utils.update_utils.upload_update_swu_to_client(ips, upgrade_file_uri[0],
                                                               utils.update_utils.update_client_callback)
            else:
                return
        elif q.text() == "Remove file from playlist":
            # log.debug("%s", self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y()).text(0))
            item = self.medialist_page.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            parent = item.parent()
            remove_file_name = item.text(0)
            remove_from_playlist = parent.text(0)
            log.debug("remove_file_name : %s", remove_file_name)
            log.debug("remove_from_playlist : %s", remove_from_playlist)
            for i in range(parent.childCount()):
                if parent.child(i).text(0) == remove_file_name:
                    self.media_engine.remove_from_playlist(remove_from_playlist, i)
                    break
        elif q.text() == "Remove Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            remove_playlist_name = item.text(0)
            self.media_engine.del_playlist(remove_playlist_name)
        elif q.text() == "Play Playlist":
            item = self.file_tree.itemAt(self.right_clicked_pos.x(), self.right_clicked_pos.y())
            play_playlist_name = item.text(0)
            self.media_engine.play_playlsit(play_playlist_name)
        elif q.text() == "test":
            for c in self.clients:
                if c.client_ip == self.right_click_select_client_ip:
                    log.debug("ready to send command")
                    cmd = "get_version"
                    param = "get_version"
                    c.send_cmd(cmd=cmd, cmd_seq_id=self.cmd_seq_id_increase(), param=param)

    def play_playlist_trigger(self):
        log.debug("")
        self.play_type = play_type.play_playlist
        thread_1 = threading.Thread(target=utils.ffmpy_utils.ffmpy_execute_list, args=(self, self.media_play_list,))
        thread_1.start()

    def stop_media_set(self):
        log.debug("")
        self.media_engine.stop_play()

    def pause_media_trigger(self):
        """check the popen subprocess is alive or not"""
        if self.media_engine.media_processor.play_status == play_status.playing:
            self.media_engine.pause_play()
            self.btn_pause.setText("Resume")
        elif self.media_engine.media_processor.play_status == play_status.pausing:
            self.media_engine.resume_play()
            self.btn_pause.setText("Pause")

    def pause_media_set(self):
        self.media_engine.pause_play()

    def resume_media_set(self):
        self.media_engine.resume_play()

    def repeat_option_set(self, repeat_value):
        self.play_option_repeat = repeat_value
        self.media_engine.media_processor.set_repeat_option(self.play_option_repeat)
        import routes
        routes.route_set_repeat_option(self.play_option_repeat)
        log.debug("self.play_option_repeat : %d", self.play_option_repeat)

    def mouseMoveEvent(self, event):
        if self.media_preview_widget is None:
            return
        # log.debug("mouseMoveEvent")
        if self.media_preview_widget.isVisible() is True:
            self.media_preview_widget.hide()
            self.preview_file_name = ""
        if self.port_layout_information_widget.isVisible() is True:
            self.port_layout_information_widget.hide()

    '''media page mouse move slot'''
    def led_client_layout_mouse_move(self, event):
        if self.led_client_layout_tree.itemAt(event.x(), event.y()) is None:
            if self.port_layout_information_widget.isVisible() is True:
                self.port_layout_information_widget.hide()
            return
        if self.led_client_layout_tree.itemAt(event.x(), event.y()).text(0).startswith("id"):
            if self.port_layout_information_widget.isVisible() is True:
                self.port_layout_information_widget.hide()
        else:
            self.port_layout_information_widget.setText("port layout :\n" +
                                                        "width :\n" +
                                                        "height :\n" +
                                                        "layout_type :\n" +
                                                        "start_point :\n")

            self.port_layout_information_widget.setGeometry(
                self.x() + self.right_frame.x() + self.led_client_layout_tree.x() + event.x() + 200,
                self.y() + self.right_frame.y() + self.led_client_layout_tree.y() + event.y() + 100,
                320, 240)
            self.port_layout_information_widget.show()

    '''media page mouse move slot'''
    def media_page_mousemove(self, event):
        try:
            self.grabMouse()
            if self.medialist_page.file_tree.itemAt(event.x(), event.y()) is None:
                if self.media_preview_widget.isVisible() is True:
                    self.media_preview_widget.hide()
                self.releaseMouse()
                return
            self.preview_file_name = self.medialist_page.file_tree.itemAt(event.x(), event.y()).text(0)

            thumbnail_file_name = hashlib.md5(
                self.preview_file_name.split(".")[0].encode('utf-8')).hexdigest() + ".webp"
            if os.path.exists(
                    internal_media_folder + ThumbnailFileFolder + thumbnail_file_name) is False:
                if self.media_preview_widget.isVisible() is True:
                    self.media_preview_widget.hide()
                self.releaseMouse()
                return
            else:
                self.media_preview_widget.setGeometry(self.medialist_page.file_tree.x() + event.x(),
                                                      self.medialist_page.file_tree.y() + event.y(), 320, 240)

                self.movie = QMovie(
                    internal_media_folder + ThumbnailFileFolder + thumbnail_file_name)

                self.media_preview_widget.setMovie(self.movie)
                self.movie.start()
                self.media_preview_widget.show()
        except Exception as e:
            log.debug(e)
        finally:
            self.releaseMouse()

    def cmd_seq_id_lock(self):
        self.cmd_seq_id_mutex.lock()

    def cmd_seq_id_unlock(self):
        self.cmd_seq_id_mutex.unlock()

    ''' cmd seqid increase method
        cmd seqid range : 0~65535'''
    def cmd_seq_id_increase(self):
        self.cmd_seq_id_lock()
        self.cmd_send_seq_id += 1
        if self.cmd_send_seq_id >= 65535:
            self.cmd_send_seq_id = 0
        self.cmd_seq_id_unlock()
        # log.debug("self.cmd_send_seq_id :%d", self.cmd_send_seq_id)
        return self.cmd_send_seq_id

    def cmd_reply_callback(self, ret, recvData=None, client_ip=None, client_reply_port=None):
        log.debug("ret :%s", ret)

    """Just for Test random command trigger"""
    def cmd_test(self, arg):
        while True:

            for c in self.clients:
                for i in range(4):
                    if i == 4:
                        cmd = "spec_test"
                    elif i == 3:
                        cmd = "set_cabinet_size"
                    elif i == 2:
                        cmd = "set_led_size"
                    elif i == 1:
                        cmd = "get_pico_num"
                    elif i == 0:
                        cmd = "get_version"
                    param = "abcde"
                    c.send_cmd(cmd=cmd, cmd_seq_id=self.cmd_seq_id_increase(), param=param)
                    time.sleep(0.1)

    def client_send_cmd_ret(self, ret, send_cmd, recv_data=None, client_ip=None, client_reply_port=None):
        if ret is False:
            log.fatal("client_ip : %s", client_ip)
            # self.send_cmd_fail_msg.hide()
            if self.send_cmd_fail_msg is not None:
                try:
                    self.send_cmd_fail_msg.setIcon(QMessageBox.Critical)
                    self.send_cmd_fail_msg.setText("Error")
                    self.send_cmd_fail_msg.setInformativeText(
                        "Can not get response of " + send_cmd + " from " + client_ip)
                    self.send_cmd_fail_msg.setWindowTitle("Error")
                    self.send_cmd_fail_msg.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                    self.send_cmd_fail_msg.show()
                except Exception as e:
                    log.fatal(e)
        else:
            if send_cmd.startswith("get"):
                if client_ip is not None:
                    for c in self.clients:
                        if c.client_ip == client_ip:
                            c.parse_get_cmd_reply(send_cmd, recv_data)

            elif send_cmd.startswith("set"):
                pass
                '''if send_cmd == "set_cabinet_params":
                    for c in self.clients:
                        if c.client_ip == client_ip:

                            param_str = "port_id:" + str(0)
                            c.send_cmd(cmd=cmd_get_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(),
                                       param=param_str)'''
            # log.debug('send_cmd : %s', send_cmd)
            # log.debug('recv_data : %s', recv_data)
            pass

    def page_status_change(self):
        if self.page_idx == 0:
            self.page_status.showMessage("Client Page")
        elif self.page_idx == 1:
            self.page_status.showMessage("Meida Page")
        elif self.page_idx == 2:
            self.page_status.showMessage("LED Setting Page")
        elif self.page_idx == 3:
            self.page_status.showMessage("HDMI-in Page")

        '''如果不是在led setting 頁面,把layout視窗關閉'''
        if self.page_idx != 3:
            if self.led_layout_window.isVisible() is True:
                self.led_layout_window.hide()

    def set_led_wall_size(self):
        ori_text_blank_jpg_uri = internal_media_folder + SubtitleFolder + subtitle_blank_jpg
        neo_text_blank_jpg_uri = internal_media_folder + subtitle_blank_jpg
        self.led_wall_width = int(self.led_setting_width_editbox.text())
        self.led_wall_height = int(self.led_setting_height_editbox.text())
        log.debug("%d", self.led_wall_width)
        log.debug("%d", self.led_wall_height)
        for i in range(5):
            try:
                utils.ffmpy_utils.neo_ffmpy_scale(ori_text_blank_jpg_uri, neo_text_blank_jpg_uri,
                                                  self.led_wall_width, self.led_wall_height)
            except Exception as e:
                log.debug(e)

            if utils.ffmpy_utils.check_media_res(neo_text_blank_jpg_uri, self.led_wall_width, self.led_wall_height):
                log.debug("neo_text_blank_jpg_uri check ok!")
                break

        self.led_config.set_led_wall_res(self.led_wall_width, self.led_wall_height)
        self.media_engine.media_processor.output_width = int(self.led_setting_width_editbox.text())
        self.media_engine.media_processor.output_height = int(self.led_setting_height_editbox.text())
        self.led_layout_window.change_led_wall_res(self.led_wall_width,
                                                   self.led_wall_height,
                                                   default_led_wall_margin)

    def set_led_wall_brightness(self):
        self.led_wall_brightness = int(self.led_brightness_editbox.text())

    '''pop-up cabinet_setting_window while client_layout_tree clicked'''
    def cabinet_setting_window_show(self, a0: QModelIndex) -> None:
        if self.led_client_layout_tree.itemFromIndex(a0).parent().text(0) is None:
            return
        log.debug("%s", self.led_client_layout_tree.itemFromIndex(a0).text(0))
        log.debug("%s", self.led_client_layout_tree.itemFromIndex(a0).parent().text(0))

        client_ip_selected = self.led_client_layout_tree.itemFromIndex(a0).parent().text(0).split("ip:")[1].split(")")[
            0]

        log.debug(a0.row())
        for c in self.clients:
            if c.client_ip == client_ip_selected:
                try:
                    for i in range(len(c.cabinets_setting)):
                        if i != a0.row():
                            # 沒有被選中的為紅色
                            self.draw_cabinet_label(c.cabinets_setting[i], Qt.GlobalColor.red)
                        else:
                            # 被選中的為黃色
                            self.draw_cabinet_label(c.cabinets_setting[i], Qt.GlobalColor.yellow)
                    if self.cabinet_setting_window is not None:
                        self.cabinet_setting_window.set_params(c.cabinets_setting[a0.row()])
                    else:
                        self.cabinet_setting_window = CabinetSettingWindow(c.cabinets_setting[a0.row()])
                    self.cabinet_setting_window.show()
                except Exception as e:
                    log.error(e)

                break

    def set_cabinet_params(self, c_params):
        log.debug('c_params.client_ip : %s', c_params.client_ip)
        log.debug('c_params.port_id : %d', c_params.port_id)
        for c in self.clients:
            if c.client_ip == c_params.client_ip:
                log.debug('')
                # c.cabinets_setting[c_params.port_id] = c_params
                c.set_cabinets(c_params)
                params_str = c.cabinets_setting[c_params.port_id].params_to_string()
                log.debug("params_str : %s", params_str)
                '''send params to client'''
                c.send_cmd(cmd=cmd_set_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(), param=params_str)

        # check
        for c in self.clients:
            if c.client_ip == c_params.client_ip:
                log.debug("c.cabinets_setting[c_params.port_id].cabinet_width = %d",
                          c.cabinets_setting[c_params.port_id].cabinet_width)
                log.debug("c.cabinets_setting[c_params.port_id].cabinet_height = %d",
                          c.cabinets_setting[c_params.port_id].cabinet_height)
                log.debug("c.cabinets_setting[c_params.port_id].start_x = %d",
                          c.cabinets_setting[c_params.port_id].start_x)
                log.debug("c.cabinets_setting[c_params.port_id].start_y = %d",
                          c.cabinets_setting[c_params.port_id].start_y)

        self.sync_client_layout_params(True, False, False)

    '''slot for signal_draw_temp_cabinet from cabinet_setting_window'''
    def draw_cabinet_label(self, c_params, qt_line_color):
        if self.led_layout_window is not None:
            log.debug('')
            '''send another signal to led_layout_window to draw the new cabinet layout'''
            self.signal_redraw_cabinet_label.emit(c_params, qt_line_color)
            # self.led_layout_window.redraw_cabinet_label(c_params)

    '''slot for signal_set_default_cabinet_resolution from cabinet_setting_window'''
    def set_default_cabinet_resolution(self, width, height):
        log.debug("")
        for c in self.clients:
            for c_param in c.cabinets_setting:
                c_param.cabinet_width = width
                c_param.cabinet_height = height

    def send_cmd_set_cabinet_params(self, c_params):
        # select the client
        for c in self.clients:
            if c.client_ip is c_params.client_ip:
                str_params = 'port_id=' + str(c_params.port_id) + ',cabinet_width=' + str(c_params.cabinet_width) + \
                             ',cabinet_height=' + str(c_params.cabinet_height) + \
                             ',start_x=' + str(c_params.start_x) + \
                             ',start_y=' + str(c_params.start_y) + \
                             ',layout_type=' + str(c_params.layout_type)

                c.send_cmd(cmd=cmd_set_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(), param=str_params)
                break

    def sync_client_cabinet_params(self, ip, force_or_not):
        # ip = "192.168.0.10" #test
        for c in self.clients:
            if c.client_ip == ip:
                for i in range(c.num_of_cabinet):
                    param_str = "port_id:" + str(i)
                    c.send_cmd(cmd=cmd_get_cabinet_params, cmd_seq_id=self.cmd_seq_id_increase(), param=param_str)

    # re-modified the playlist tree widget
    # 增加用media_file_uri, 移除用index
    def playlist_changed(self, changed_or_not, playlist_name, media_file_uri, index, action):
        log.debug("playlist_changed")
        # 如果需要更新
        if changed_or_not is True:
            # 如果是新playlist
            if action == self.media_engine.ACTION_TAG_ADD_NEW_PLAYLIST:
                tmp_new_playlist = QTreeWidgetItem()
                tmp_new_playlist.setText(0, playlist_name)
                tmp_new_file_uri = QTreeWidgetItem()
                tmp_new_file_uri.setText(0, os.path.basename(media_file_uri))
                tmp_new_playlist.addChild(tmp_new_file_uri)
                tmp_new_playlist.setExpanded(True)
                self.medialist_page.qtw_media_play_list.addChild(tmp_new_playlist)

            else:
                '''先尋找是否已經存在playlist,如果有就掃描加入'''
                for i in range(self.medialist_page.qtw_media_play_list.childCount()):
                    #print(self.medialist_page.qtw_media_play_list.child(i).text(0))
                    if self.medialist_page.qtw_media_play_list.child(i).text(0) == playlist_name:
                        if action == self.media_engine.ACTION_TAG_ADD_MEDIA_FILE:
                            file_name_item = QTreeWidgetItem(self.medialist_page.qtw_media_play_list.child(i))
                            file_name_item.setText(0, os.path.basename(media_file_uri))
                            self.medialist_page.qtw_media_play_list.child(i).addChild(file_name_item)
                            return
                        elif action == self.media_engine.ACTION_TAG_REMOVE_MEDIA_FILE:
                            playlist_tmp = self.medialist_page.qtw_media_play_list.child(i)
                            remove_item = playlist_tmp.child(index)
                            playlist_tmp.removeChild(remove_item)
                            return
                        elif action == self.media_engine.ACTION_TAG_REMOVE_ENTIRE_PLAYLIST:
                            playlist_tmp = self.medialist_page.qtw_media_play_list.child(i)
                            self.medialist_page.qtw_media_play_list.removeChild(playlist_tmp)
                            return

    def external_medialist_changed(self, changed_or_not):
        log.debug("external_medialist_changed")
        '''如果需要更新,要全部掃描一次'''
        if changed_or_not is True:
            for i in range(self.medialist_page.external_media_root.childCount()):
                self.medialist_page.external_media_root.removeChild(self.medialist_page.external_media_root.child(i))
            child_count = 0
            for external_media_list in self.media_engine.external_medialist:
                external_folder = QTreeWidgetItem()
                external_folder.setText(0, os.path.basename(external_media_list.folder_uri))
                self.medialist_page.external_media_root.addChild(external_folder)
                for f in external_media_list.filelist:
                    external_file_item = QTreeWidgetItem()
                    external_file_item.setText(0, os.path.basename(f))
                    utils.ffmpy_utils.gen_webp_from_video(external_media_list.folder_uri,
                                                          os.path.basename(f))  # need to remove later
                    self.medialist_page.external_media_root.child(child_count).addChild(external_file_item)
                self.medialist_page.external_media_root.child(child_count).setExpanded(True)
                child_count += 1

    def internaldef_medialist_changed(self):
        log.debug("self.medialist_page.internal_media_root.childCount() = %d",
                  self.medialist_page.internal_media_root.childCount())
        self.media_engine.refresh_internal_medialist()

        self.medialist_page.refresh_internal_medialist()

    def slot_new_playlist(self, new_playlist_name):
        log.debug("")
        new_playlist_name += '.playlist'
        # self.media_engine.new_playlist(new_playlist_name)
        self.media_engine.add_to_playlist(new_playlist_name, self.medialist_page.right_clicked_select_file_uri)

    def focus_on_window_changed(self):

        if self.isActiveWindow() is False:
            if self.media_preview_widget.isVisible() is True:
                self.media_preview_widget.hide()



class MyDelegate(QItemDelegate):
    def __init__(self):
        QItemDelegate.__init__(self)

    def sizeHint(self, option, index):
        return QSize(32, 32)
