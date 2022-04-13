import glob
import utils.log_utils
import os
import pyudev
import psutil
import pyinotify
from global_def import *

from subprocess import check_output, CalledProcessError

log = utils.log_utils.logging_init(__file__)

def get_media_file_list(dir, with_path=False):
    log.error("dir : %s", dir)
    file_list = glob.glob(dir + "/*.mp4") + glob.glob(dir + "/*.jpg") + glob.glob(dir + "/*.jpeg") + glob.glob(dir + "/*.png")

    return file_list

def get_playlist_file_list(dir, with_path=False):
    log.debug("dir : %s", dir)
    file_list = glob.glob(dir + "/*.playlist")

    return file_list


def get_mount_points(devices=None):
    context = pyudev.Context()

    mount_points = []
    # 分割磁區的pen drive
    removable = [device for device in context.list_devices(subsystem='block', devtype='partition') if
                 device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in
                      context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]

        for p in psutil.disk_partitions():
            if p.device in partitions:
                mount_points.append(p.mountpoint)

    # 未分割磁區的pen drive
    for device in removable:
        partitions = [device.device_node for device in
                      context.list_devices(subsystem='block', DEVTYPE='disk', parent=device)]

        for p in psutil.disk_partitions():
            if p.device in partitions:
                mount_points.append(p.mountpoint)
    return mount_points

def change_text_content(content):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_file_name, 'w')
    config_file.write(content)
    os.system("sync")

def change_text_size(size):
    config_file = open(internal_media_folder + SubtitleFolder + subtitle_size_file_name, 'w')
    config_file.write(size)
    os.system("sync")





