import subprocess

from PyQt5.QtCore import QThread, pyqtSignal, QDateTime, QObject, QTimer, QMutex
import utils.log_utils
import utils.net_utils
import os
import platform

log = utils.log_utils.logging_init(__file__)


class TC358743(QObject):
	# connected, width, height, fps
	signal_refresh_tc358743_param = pyqtSignal(bool, int, int, int)

	def __init__(self, **kwargs):
		super(TC358743, self).__init__(**kwargs)

		self.hdmi_connected = None
		self.hdmi_width = None
		self.hdmi_height = None
		self.hdmi_fps = None
		self.res_set_dv_bt_timing = False
		if platform.machine() in ('arm', 'arm64', 'aarch64'):
			self.check_hdmi_status_mutex = QMutex()
		else:
			self.check_hdmi_status_mutex = None
		self.hdmi_connected, self.hdmi_width, self.hdmi_height, self.hdmi_fps = self.get_tc358743_dv_timing()
		self.res_set_dv_bt_timing = self.set_tc358743_dv_bt_timing()

	def reinit_tc358743_dv_timing(self):
		log.debug("")
		self.hdmi_connected, self.hdmi_width, self.hdmi_height, self.hdmi_fps = self.get_tc358743_dv_timing()
		self.signal_refresh_tc358743_param.emit(self.hdmi_connected, self.hdmi_width, self.hdmi_height, self.hdmi_fps)

	def check_hdmi_status_lock(self):
		if self.check_hdmi_status_mutex is not None:
			self.check_hdmi_status_mutex.lock()

	def check_hdmi_status_unlock(self):
		if self.check_hdmi_status_mutex is not None:
			self.check_hdmi_status_mutex.unlock()

	def x86_get_video0_timing(self):
		log.debug("")
		connect = False
		p = os.popen("lsusb").read()
		log.debug("lsusb : %s", p)
		if '22d9:2765' not in p:
			return connect, 0, 0, 0
		ffprobe_v4l2 = subprocess.Popen("ffprobe -hide_banner /dev/video0", shell=True, stdout=subprocess.PIPE,
		                                stderr=subprocess.PIPE)
		stdout, stderr = ffprobe_v4l2.communicate()

		data = stderr.decode().split(", ")
		for s in data:
			# log.debug("s:%s", s)
			if '640x480' in s:
				connected = True
		return connected, 640, 480, 30

	def get_tc358743_dv_timing(self):
		log.debug("")
		connected = False
		width = 0
		height = 0
		fps = 0
		if platform.machine() in ('arm', 'arm64', 'aarch64'):
			pass
		else:
			connected, width, height, fps = self.x86_get_video0_timing()
			return connected, width, height, fps
		self.check_hdmi_status_lock()
		dv_timings = os.popen("v4l2-ctl --query-dv-timings").read()
		self.check_hdmi_status_unlock()
		list_dv_timings = dv_timings.split("\n")

		if 'fail' in list_dv_timings[0]:
			log.debug("not connected")
			connected = False
			
			self.signal_refresh_tc358743_param.emit(connected, width, height, fps)
			return connected, width, height, fps
		else:
			connected = True
		if connected is True:
			for i in list_dv_timings:
				if 'Active width:' in i:
					width = int(i.split(":")[1])
				if 'Active height:' in i:
					height = int(i.split(":")[1])
				if 'Pixelclock' in i:
					fps = int(float(i.split("(")[1].split(" ")[0]))

		# log.debug("width = %d", width)
		# log.debug("height = %d", height)
		# log.debug("fps = %d", fps)
		self.signal_refresh_tc358743_param.emit(connected, width, height, fps)
		return connected, width, height, fps

	def set_tc358743_dv_bt_timing(self):
		if platform.machine() in ('arm', 'arm64', 'aarch64'):
			pass
		else:
			return True
		self.check_hdmi_status_lock()
		res_set_dv_bt_timing = os.popen("v4l2-ctl --set-dv-bt-timings query").read()
		self.check_hdmi_status_unlock()
		log.debug("res_set_dv_bt_timing = %s", res_set_dv_bt_timing)
		if 'BT timings set' in res_set_dv_bt_timing:
			# log.debug("set timing OK")
			return True
		log.debug("set timing NG")
		return False

	def get_tc358743_hdmi_connected_status(self):

		connected = False
		if platform.machine() in ('arm', 'arm64', 'aarch64'):
			pass
		else:
			p = os.popen("lsusb").read()
			log.debug("lsusb : %s", p)
			if '22d9:2765' not in p:
				log.debug("not connected")
				return connected
			ffprobe_v4l2 = subprocess.Popen("ffprobe -hide_banner /dev/video0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdout, stderr = ffprobe_v4l2.communicate()

			data = stderr.decode().split(", ")
			for s in data:
				# log.debug("s:%s", s)
				if '640x480' in s:
					connected = True
			return connected
		self.check_hdmi_status_lock()
		dv_timings = os.popen("v4l2-ctl --query-dv-timings").read()
		self.check_hdmi_status_unlock()
		list_dv_timings = dv_timings.split("\n")
		# log.debug("list_dv_timings=%s", list_dv_timings)
		if 'fail' in list_dv_timings[0]:
			log.debug("not connected")
			connected = False
		else:
			connected = True
			for i in list_dv_timings:
				if 'Active width:' in i:
					width = int(i.split(":")[1])
					if width != self.hdmi_width:
						connected = False
						break
				if 'Active height:' in i:
					height = int(i.split(":")[1])
					if height != self.hdmi_height:
						connected = False
						break
				'''if 'Pixelclock' in i:
					fps = int(float(i.split("(")[1].split(" ")[0]))
					if fps != self.hdmi_fps:
						connected = False
						break'''


		return connected
