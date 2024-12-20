import enum
import platform
import os
from pathlib import Path
import utils.log_utils
log = utils.log_utils.logging_init(__file__)

"""Software version"""
version = "LS241120001"

X86_ETH_INTERFACE = 'enp55s0'

def get_led_role():
    led_role = "Server"
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        pass
    else:
        led_role = "Server"
        print("Aled_role = ", led_role)
        return led_role

    if os.path.exists("/home/root/aio_now"):
        print("AIO")
        led_role = "AIO"
        print("Aled_role = ", led_role)
        return led_role
    else:
        led_role = "Server"
    print("Bled_role = ", led_role)
    return led_role


'''Network relative'''
multicast_group = "239.11.11.11"
server_broadcast_port = 11334
server_broadcast_message = "ABCDE;Server:192.168.0.3;Cmd_Port:11335;Alive_Port:11333"
alive_report_port = 11333


if "Server" in get_led_role():
    udp_sink = "udp://239.11.11.11:15000"
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        localaddr = "192.168.0.3"
    else:
        localaddr = "192.168.0.2"

elif "AIO" in get_led_role():
    udp_sink = "udp://127.0.0.1:15000"
    localaddr = "127.0.0.1"
else:
    udp_sink = "udp://239.11.11.11:15000"
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        localaddr = "192.168.0.3"
    else:
        localaddr = "192.168.0.2"

local_sink = "udp://127.0.0.1:15001"
cv2_preview_h264_sink = "udp://127.0.0.1:10011"
cv2_preview_v4l2_sink = "/dev/video5"
hdmi_in_h264_src = "udp://127.0.0.1:10012"
cmd_timeout = 5
g_client_udp_cmd_port = 11335
flask_server_port = 9098


SIZE_MB = 1024*1024

"""Media folder"""
if platform.machine() in ('arm', 'arm64', 'aarch64'):
    internal_media_folder = "/home/root/Videos"
else:
    internal_media_folder = "/home/venom/Videos"

ThumbnailFileFolder = "/.thumbnails/"
PlaylistFolder = "/.playlists/"
SubtitleFolder = "/.subtitle_data"

init_config_file = "/.config_video_param"
subtitle_blank_jpg = "/subtitle_blank.jpg"
neo_subtitle_blank_jpg = "/neo_subtitle_blank.jpg"
subtitle_file_name = "/subtitle.dat"
subtitle_size_file_name = "/subtitle_size.dat"
subtitle_speed_file_name = "/subtitle_speed.dat"
subtitle_position_file_name = "/subtitle_position.dat"
subtitle_period_file_name = "/subtitle_period.dat"

mp4_extends = internal_media_folder + "/*.mp4"
jpeg_extends = internal_media_folder + "/*.jpeg"
jpg_extends = internal_media_folder + "/*.jpg"
png_extends = internal_media_folder + "/*.png"
webp_extends = internal_media_folder + '/*.webp'
playlist_extends = internal_media_folder + PlaylistFolder + "*.playlist"

class play_type(enum.IntEnum):
    play_none = 0
    play_single = 1
    play_playlist = 2
    play_hdmi_in = 3
    play_cms = 4

class play_status(enum.IntEnum):
    initial = -1
    stop = 0
    playing = 1
    pausing = 2


class repeat_option(enum.IntEnum):
    repeat_none = 0
    repeat_one = 1
    repeat_all = 2
    repeat_random = 3
    repeat_option_max = 3


class frame_brightness_adjust(enum.IntEnum):
    fix_mode = 0
    auto_time_mode = 1
    auto_als_mode = 2
    test_mode = 3


class hdmi_ch_switch_option(enum.IntEnum):
    hdmi_csi = 0,
    hdmi_usb = 1

day_mode_brightness = 90
night_mode_brightness = 60
sleep_mode_brightness = 0


""" UI relative"""
popmenu_font_size = 15
media_btn_width = 110

""" Cmd relative"""
cmd_spliter = ";"

"""default led params"""
default_led_wall_width = 288 #80
default_led_wall_height = 120 #144 #96
default_led_wall_brightness = 100
default_led_cabinet_width = 40
default_led_cabinet_height = 24
default_led_wall_margin = 10

"""default led client frame params"""
default_led_client_brightness = 100
default_led_client_brdivisor = 1
default_led_client_gamma = 2.2

"""right page idx"""
page_client_connect_idx = 0
page_media_content_idx = 1
page_hdmi_in_content_idx = 2
page_led_setting_idx = 3
page_cms_setting_idx = 4
page_test = 5
page_cmd_setting_idx = 6

"""ffmpy initial value"""
still_image_loop_cnt = 1
still_image_video_period = 600
preview_start_time = 3
preview_period = 3

"""ffmpeg default text font size & content"""
text_font_size_default = 16
text_font_speed_default = "Medium"
text_font_position_default = "Medium"
text_font_period_default = 20
text_content_default = 12345678

text_font_speed_slow = "Slow"
text_font_speed_medium = "Medium"
text_font_speed_fast = "Fast"

text_font_position_high = "High"
text_font_position_medium = "Medium"
text_font_position_low = "Low"

"""lcd1602 server address"""
lcd1602_server_address = '/tmp/uds_socket_i2clcd7'

"""QFont style & size"""
qfont_style_default = "Times"
qfont_style_size_extra_large = 32
qfont_style_size_large = 24
qfont_style_size_medium = 18


web_cmd_interval = 3

'''for cms, waiting all clinet connected to trigger default launch type'''
total_num_of_clients = 2


def aio_set_total_num_of_clients():
    global total_num_of_clients
    total_num_of_clients = 1


def get_total_num_of_clients():
    global total_num_of_clients
    return total_num_of_clients

fps_30="30/1"
fps_25="25/1"
fps_23="23/1"
fps_15="15/1"
fps_10="10/1"
fps_1="1/1"
target_fps=fps_23

FUNCTION_DISABLE = False

refresh_clients_thread_interval = 10

"""default hdmi ch switch params"""
default_hdmi_ch_switch = hdmi_ch_switch_option.hdmi_csi.value
hdmi_not_find_device = False
default_hdmi_csi_ch_device = hdmi_not_find_device
default_hdmi_usb_ch_device = hdmi_not_find_device

default_video_capture_card_id = "534d:2109"
default_video_capture_card_width = 640
default_video_capture_card_height = 480
default_video_capture_card_fps = 30


