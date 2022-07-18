import subprocess
from PyQt5.QtCore import QTimer, QMutex
from PyQt5 import QtCore
from time import sleep
import utils.log_utils

log = utils.log_utils.logging_init(__file__)

#This component only handles the bt device agent discovery/pair action

class BlueTooth(QtCore.QThread):
	def __init__(self,parent=None):
		super().__init__(parent)
		self.bt_status = "waiting_for_pair"
		self.bt_process = None

	def run(self):
		try:
			subprocess.Popen("hciconfig hci0 sspmode 1", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("hciconfig hci0 sspmode", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl discoverable on", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl pair on", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			self.bt_process = subprocess.Popen("bluetoothctl", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
		except Exception as e:
			log.debug(e)
		try:
			self.write(self.bt_process, "agent off")
			log.debug(self.read(self.bt_process))
			self.write(self.bt_process, "agent NoInputNoOutput")
			log.debug(self.read(self.bt_process))
			self.write(self.bt_process, "default-agent")
			log.debug(self.read(self.bt_process))
			self.write(self.bt_process, "discoverable on")
			log.debug(self.read(self.bt_process))
			self.write(self.bt_process, "pairable on")
			log.debug(self.read(self.bt_process))
		except Exception as e:
			log.debug(e)

		while True:
			log.debug("bt running")
			sleep(20)
			try:
				readline = self.read(self.bt_process)
				log.debug(readline)
				if "yes/no" in readline:
					self.write(self.bt_process, "yes")
			except Exception as e:
				log.debug(e)

	def read(self, process):
		return process.stdout.readline().decode("utf-8").strip()

	def write(self, process, message):
		process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
		process.stdin.flush()