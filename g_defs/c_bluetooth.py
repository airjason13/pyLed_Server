import os
import signal
import subprocess
from PyQt5.QtCore import QTimer, QMutex
from PyQt5 import QtCore
from time import sleep
import utils.log_utils

log = utils.log_utils.logging_init(__file__)


# This component only handles the bt device agent discovery/pair action
class BlueTooth(QtCore.QThread):
	def __init__(self,parent=None):
		super().__init__(parent)
		self.bt_status = "waiting_for_pair"
		self.bt_process = None
		self.bt_comm = None
		self.loop_count = 0
		self.discoverable_launch_threshold = 10

	def run(self):
		self.kill_simple_agent()
		self.kill_rfcomm_servver_sdp()
		self.clear_bt_devices()

		try:
			subprocess.Popen("hciconfig hci0 sspmode 1", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("hciconfig hci0 sspmode", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl discoverable on", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl pair on", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			self.bt_process = subprocess.Popen("/usr/lib/bluez/test/simple-agent", shell=True, stdin=subprocess.PIPE,
			                                   stdout=subprocess.PIPE,
			                                   stderr=subprocess.PIPE)
			self.bt_comm = os.popen('rfcomm-server-sdp.py')

		except Exception as e:
			log.debug(e)
		while True:
			self.loop_count = self.loop_count + 1
			if self.loop_count > self.discoverable_launch_threshold:
				self.bt_set_discoverable()
			try:
				process = os.popen('pgrep -f simple-agent')
				p_read = process.read()
				if len(p_read) > 0:
					pass
					#log.debug("rfcomm-server-sdp.py pid = %s", p_read)
				else:
					self.bt_process = subprocess.Popen("/usr/lib/bluez/test/simple-agent", shell=True,
					                                   stdin=subprocess.PIPE,
					                                   stdout=subprocess.PIPE,
					                                   stderr=subprocess.PIPE)
				process.close()
				process = os.popen('pgrep -f rfcomm-server-sdp.py')
				p_read = process.read()
				if len(p_read) > 0:
					pass
					#log.debug("rfcomm-server-sdp.py pid = %s", p_read)
				else:
					log.debug("no rfcomm-server-sdp.py running")
					self.bt_comm = None
					self.bt_comm = os.popen('rfcomm-server-sdp.py')
					self.clear_bt_devices()
				process.close()
			except Exception as e:
				log.debug(e)

			sleep(2)


	def readstdout(self, process):
		res = process.stdout.readline().decode("utf-8").strip()
		return res

	def readstderr(self, process):
		res = process.stderr.readline().decode("utf-8").strip()
		return res

	def write(self, process, message):
		process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
		process.stdin.flush()

	def clear_bt_devices(self):
		process = os.popen('bluetoothctl devices')
		p_read = process.read()
		if len(p_read) > 0:
			log.debug(p_read)
			log.debug("str len: %d", len(p_read))
			process.close()
			dev_addr = p_read.split(" ")[1]
			log.debug(p_read)
			process = os.popen('bluetoothctl remove ' + dev_addr)
			p_read = process.read()
			log.debug(p_read)
			process.close()
		else:
			process.close()

	def bt_set_discoverable(self):
		log.debug("")
		process = os.popen('bluetoothctl discoverable on')
		p_read = process.read()
		process.close()

	def kill_simple_agent(self):
		process = os.popen('pgrep -f simple-agent.py')
		p_read = process.read()
		log.debug("pread : %s", p_read)
		if len(p_read) > 0:
			pid_list = p_read.split("\n")
			log.debug("pid_list : %s", pid_list)
			for i in pid_list:
				if len(i) > 0:
					log.debug("pid = %d", int(i))
					os.kill(int(i), signal.SIGTERM)
		process.close()

	def kill_rfcomm_servver_sdp(self):
		process = os.popen('pgrep -f rfcomm-server-sdp.py')
		p_read = process.read()
		if len(p_read) > 0:
			pid_list = p_read.split("\n")
			for i in pid_list:
				if len(i) > 0:
					os.kill(int(i), signal.SIGTERM)
		process.close()
