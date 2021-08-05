import glob
import utils.log_utils
import os
import pyudev
import psutil

from subprocess import check_output, CalledProcessError

log = utils.log_utils.logging_init('file_utils')

def get_media_file_list(dir, with_path=False):
    log.error("dir : %s", dir)
    file_list = glob.glob(dir + "/*.mp4")

    return file_list



def get_mount_points(devices=None):
    context = pyudev.Context()

    mount_points = []
    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if
                 device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in
                      context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
        print("All removable partitions: {}".format(", ".join(partitions)))
        print("Mounted removable partitions:")
        for p in psutil.disk_partitions():
            if p.device in partitions:
                print("  {}: {}".format(p.device, p.mountpoint))
                mount_points.append(p.mountpoint)

    return mount_points
