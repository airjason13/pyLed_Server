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
			subprocess.Popen("bluetoothctl --agent=NoInputNoOutput", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			                 stderr=subprocess.PIPE)
		except Exception as e:
			log.debug(e)
		while True:
			log.debug("bt running")
			sleep(20)
			try:
				subprocess.Popen("bluetoothctl discoverable on", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
				                 stderr=subprocess.PIPE)
				subprocess.Popen("bluetoothctl pair on", stdin=subprocess.PIPE, stdout=subprocess.PIPE,
				                 stderr=subprocess.PIPE)
			except Exception as e:
				log.debug(e)
