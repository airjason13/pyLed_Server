import enum
import platform

version="LS210805A01"
multicast_group="239.11.11.11"
server_broadcast_port=11334
server_broadcast_message="Server:192.168.0.3,Cmd_Port:11335,Alive_Port:11333"
alive_report_port=11333
cmd_port=11335


udp_sink = "udp://239.11.11.11:15000"

if platform.machine() in ('arm', 'arm64', 'aarch64'):
    internal_media_folder="/home/root/Videos"
else:
    internal_media_folder="/home/venom/Videos"

ThumbnailFileFolder = "/.thumbnails/"

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



