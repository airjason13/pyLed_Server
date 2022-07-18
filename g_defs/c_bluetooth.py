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
			log.debug(self.readstdout(self.bt_process))
			log.debug(self.readstderr(self.bt_process))
			self.write(self.bt_process, "agent NoInputNoOutput")
			log.debug(self.readstdout(self.bt_process))
			log.debug(self.readstderr(self.bt_process))
			self.write(self.bt_process, "default-agent")
			log.debug(self.readstdout(self.bt_process))
			log.debug(self.readstderr(self.bt_process))
			self.write(self.bt_process, "discoverable on")
			log.debug(self.readstdout(self.bt_process))
			log.debug(self.readstderr(self.bt_process))
			self.write(self.bt_process, "pairable on")
			log.debug(self.readstdout(self.bt_process))
			log.debug(self.readstderr(self.bt_process))
		except Exception as e:
			log.debug(e)

		while True:
			log.debug("bt running")
			
			try:
				readline_stdout = self.readstdout(self.bt_process)
				log.debug(readline_stdout)
				if "yes/no" in readline_stdout:
					self.write(self.bt_process, "yes")
				readline_stderr = self.readstderr(self.bt_process)
				log.debug(readline_stderr)
				if "yes/no" in readline_stderr:
					self.write(self.bt_process, "yes")
			except Exception as e:
				log.debug(e)

	def readstdout(self, process):
		while True:
			res = process.stdout.readline().decode("utf-8").strip()
			if len(res) > 0:
				break
		return res

	def readstderr(self, process):
		while True:
			res = process.stderr.readline().decode("utf-8").strip()
			if len(res) > 0:
				break
		return res

	def write(self, process, message):
		process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
		process.stdin.flush()