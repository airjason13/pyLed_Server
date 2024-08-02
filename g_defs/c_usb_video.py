import subprocess
from PyQt5.QtCore import QObject
from global_def import *


class VideoCaptureCard(QObject):

    def __init__(self, **kwargs):
        super(VideoCaptureCard, self).__init__(**kwargs)
        self.hdmi_connected = None
        self.video_device = None

        video_device = self.find_video_device(default_video_capture_card_id)
        width = default_video_capture_card_width
        height = default_video_capture_card_height
        fps = default_video_capture_card_fps

        self.update_video_device(video_device)
        if self.get_usb_hdmi_connected_status():
            self.set_video_out_timing(video_device, width, height, fps)

    def set_video_out_timing(self, device, width, height, fps):
        try:
            subprocess.run(
                ['v4l2-ctl', f'--device={device}', f'--set-fmt-video=width={width},height={height},pixelformat=MJPG'],
                check=True)
            subprocess.run(['v4l2-ctl', f'--device={device}', f'--set-parm={fps}'], check=True)
            log.debug(f"Video output timing set: device={device}, width={width}, height={height}, fps={fps}")
        except subprocess.CalledProcessError as e:
            log.debug(f"Failed to set video output timing: {e}")

    def find_video_device(self, device_id):
        result = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
        output = result.stdout.split('\n')

        device_index = -1
        for i, line in enumerate(output):
            if device_id in line:
                device_index = i
                break

        if device_index != -1 and device_index + 1 < len(output):
            device_info = output[device_index + 1].strip()
            if '/dev/video' in device_info:
                return device_info.split()[0]

        return "not_found"

    def update_video_device(self, video_device):
        if video_device != "not_found":
            self.video_device = video_device
            self.hdmi_connected = True
        else:
            self.video_device = default_hdmi_usb_ch_device
            self.hdmi_connected = False

    def get_video_device(self):
        return self.video_device

    def get_usb_hdmi_connected_status(self):
        return self.hdmi_connected
