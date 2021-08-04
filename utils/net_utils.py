import socket
import fcntl
import struct
import netifaces as ni
import utils.log_utils

log = utils.log_utils.logging_init()

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode())
        )[20:24])
    except Exception as e:
        log.error(e)
        ip = ""
    finally:
        return ip

def get_ip_address_by_nic(ifname):
    ni.ifaddresses(ifname)
    ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    print(ip)
