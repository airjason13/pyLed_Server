import socket
import fcntl
import struct
import netifaces as ni
import utils.log_utils
from global_def import *
import platform
import os

log = utils.log_utils.logging_init(__file__)

def get_ip_address():
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        ifname = 'eth0'
    else:
        ifname = 'enp2s0'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode())
        )[20:24])
    except Exception as e:

        ip = ""
    finally:
        return ip


def get_ip_address_by_nic(ifname):
    ni.ifaddresses(ifname)
    ip = ni.ifaddresses(ifname)[ni.AF_INET][0]['addr']
    print(ip)


#def send_udp_cmd( server_ip, client_ip, client_port, cmd, cmd_seq_id, param, cb):
def send_udp_cmd(*args, **kwargs):
    log.debug("kwargs : %s", kwargs)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_ip = kwargs.get('client_ip')
    server_ip = kwargs.get('server_ip')
    cmd = kwargs.get('cmd')
    cmd_seq_id = kwargs.get('cmd_seq_id')
    client_udp_cmd_port = kwargs.get('client_udp_cmd_port')
    param = kwargs.get('param')
    cb = kwargs.get('cb')
    try:
        sock.bind((server_ip, 0))
        cmd_str = 'cmd_seq_id:' + str(cmd_seq_id) + cmd_spliter + "cmd:" + cmd + cmd_spliter + "param:" + param

        sendDataLen = sock.sendto(cmd_str.encode(), (client_ip, client_udp_cmd_port))
        log.debug("send cmd len : %d", sendDataLen)
        sock.settimeout(cmd_timeout)

        revcData, (remoteHost, remotePort) = sock.recvfrom(1024)
        log.debug("recv from [%s:%s] " % (remoteHost, remotePort))
        recv_cmd_seq_id = revcData.decode().split(";")[0].split(":")[1]
        log.debug("recv_cmd_seq_id %s", recv_cmd_seq_id)
        if int(recv_cmd_seq_id) != cmd_seq_id:
            log.fatal("cmd_seq_id error")
            log.fatal("cmd_seq_id : %d", cmd_seq_id)
            #log.fatal("int(recv_cmd_seq_id): %d", int(recv_cmd_seq_id))
            cb(False, cmd )
        else:    
            cb( True, cmd, recvData=revcData.decode(), client_ip=remoteHost, client_reply_port=remotePort)
    except Exception as e:
        #log.fatal("cmd_seq_id error")
        log.fatal("cmd_seq_id : %d", cmd_seq_id)
        #log.fatal("int(recv_cmd_seq_id): %d", int(recv_cmd_seq_id))
        log.fatal(e)
        cb(False, cmd )
    finally:
        sock.close()


def force_set_eth_ip():
    ip = get_ip_address()
    if platform.machine() in ('arm', 'arm64', 'aarch64'):
        if ip == "":
            log.info("ip = NULL")
            if platform.machine() in ('arm', 'arm64', 'aarch64'):
                ifname = 'eth0'
            else:
                ifname = 'enp2s0'
            cmd = 'ifconfig' + ' ' + ifname + ' ' + '192.168.0.3'
            os.system(cmd)
