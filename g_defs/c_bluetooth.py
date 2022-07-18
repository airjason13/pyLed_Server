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
			subprocess.Popen("hciconfig hci0 sspmode 1", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("hciconfig hci0 sspmode", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl discoverable on", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			subprocess.Popen("bluetoothctl pair on", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
			self.bt_process = subprocess.Popen("bluetoothctl --agent=NoInputNoOutput", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
		except Exception as e:
			log.debug(e)
		try:
			self.write(self.bt_process, "default-agent")
			log.debug(self.read(self.bt_process))
		except Exception as e:
			log.debug(e)

		while True:
			log.debug("bt running")
			sleep(20)
			try:
				self.write(self.bt_process, "bluetoothctl discoverable on")
				log.debug(self.read(self.bt_process))
				self.write(self.bt_process, "bluetoothctl pairable on")
				log.debug(self.read(self.bt_process))
			except Exception as e:
				log.debug(e)

	def read(process):
		return process.stdout.readline().decode("utf-8").strip()

	def write(process, message):
		process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
		process.stdin.flush()