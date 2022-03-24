import enum
import platform
"""Software version"""
version = "LS220301601"

"""Network relative"""
multicast_group = "239.11.11.11"
server_broadcast_port = 11334
server_broadcast_message = "ABCDE;Server:192.168.0.3;Cmd_Port:11335;Alive_Port:11333"
alive_report_port = 11333
udp_sink = "udp://239.11.11.11:15000"
local_sink = "udp://127.0.0.1:15001"
cv2_preview_h264_sink = "udp://127.0.0.1:10011"
cv2_preview_v4l2_sink = "/dev/video5"
hdmi_in_h264_src = "udp://127.0.0.1:10012"
cmd_timeout = 2
g_client_udp_cmd_port = 11335
flask_server_port = 9090


SIZE_MB = 1024*1024

"""Media folder"""
if platform.machine() in ('arm', 'arm64', 'aarch64'):
    internal_media_folder = "/home/root/Videos"
else:
    internal_media_folder = "/home/venom/Videos"

mp4_extends = internal_media_folder + "/*.mp4"
jpeg_extends = internal_media_folder + "/*.jpeg"
jpg_extends = internal_media_folder + "/*.jpg"
png_extends = internal_media_folder + "/*.png"
webp_extends = internal_media_folder + '/*.webp'

ThumbnailFileFolder = "/.thumbnails/"
PlaylistFolder = "/.playlists/"
init_config_file = "/.config_video_param"
subtitle_file_name = "/.subtitle"

class play_type(enum.IntEnum):
    play_none = 0
    play_single = 1
    play_playlist = 2
    play_hdmi_in = 3

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

"""ffmpy initial value"""
still_image_loop_cnt = 1
still_image_video_period = 600
preview_start_time = 3
preview_period = 3


"""lcd1602 server address"""
lcd1602_server_address = '/tmp/uds_socket_i2clcd7'