import enum
import platform
"""Software version"""

"""Network relative"""
version="LS210907A01"
multicast_group="239.11.11.11"
server_broadcast_port=11334
server_broadcast_message="ABCDE;Server:192.168.0.3;Cmd_Port:11335;Alive_Port:11333"
alive_report_port=11333
#cmd_port = 11335
udp_sink = "udp://239.11.11.11:15000"
local_sink = "udp://127.0.0.1:15001"
cmd_timeout = 2
g_client_udp_cmd_port=11335


"""Media folder"""
if platform.machine() in ('arm', 'arm64', 'aarch64'):
    internal_media_folder="/home/root/Videos"
else:
    internal_media_folder="/home/venom/Videos"

ThumbnailFileFolder = "/.thumbnails/"
PlaylistFolder = "/.playlists/"

class play_type(enum.IntEnum):
    play_none = 0
    play_single = 1
    play_playlist = 2

class play_status(enum.IntEnum):
    stop = 0
    playing = 1
    pausing = 2

class repeat_option(enum.IntEnum):
    repeat_none = 0
    repeat_one = 1
    repeat_all = 2
    repeat_option_max = 2


""" UI relative"""
popmenu_font_size = 15
media_btn_width = 110

""" Cmd relative"""
cmd_spliter = ";"

"""default led params"""
default_led_wall_width = 80
default_led_wall_height = 96
default_led_wall_brightness = 100
default_led_cabinet_width = 40
default_led_cabinet_height = 24
default_led_wall_margin = 10