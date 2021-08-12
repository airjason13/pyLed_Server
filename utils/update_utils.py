import requests
import time
import asyncio
import threading
import utils.log_utils

log = utils.log_utils.logging_init('update_utils')


def request_post_upload_file(ip, swu_file_url, cb):
    log.debug("enter")
    url = "http://" + ip + ":8080/upload"
    headers ={
        #'Content-Type': 'application/octet-stream\r\n\r\n'
    }
    r = None
    files = {
        'file': (open(swu_file_url, 'rb',))
    }

    try:
        r = requests.post(url=url, files=files, timeout=10 ).text

        log.debug("r.status_code = %s", r.status_code)
        log.debug("r = %s", r)
        cb(ip, True)
        return True
    except Exception as e:
        log.error(e)
        cb(ip, False)
        return False


def upload_update_swu_to_client(ips, swu_file_url, cb):
    start_time = time.time()
    log.debug("start_time = %s", start_time)
    request_threads = [len(ips)]
    i = 0
    for ip in ips:
        request_threads[i] = threading.Thread(target=request_post_upload_file, args=(ip, swu_file_url, cb))
        request_threads[i].start()
        i += 1
    end_time = time.time()
    log.debug("end_time = %s", end_time)

def request_ret(ip, ret):
    if ret is False:
        log.error("%s request fail", ip)
    else:
        log.debug("%s request success", ip)
    """loop = asyncio.get_event_loop()
    tasks = []

    for ip in ips:
        task = loop.create_task(request_post_upload_file(ip, swu_file_url))
        tasks.append(task)
    
    loop.run_until_complete(asyncio.wait(tasks))"""


"""class Client_Update:

    def __init__(self, ip, swu_file_url):
        self.ip = ip
        self.swu_file_url = swu_file_url
        self.file = files = {
            'file': (open(self.swu_file_url, 'rb',))
        }
        self.doRequest()

    def doRequest(self):

        url = "http://" + self.ip + ":8080/upload"
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        #self.nam.get(req)
        self.nam.post(req)

    def handleResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
        else:
            print("Error occured: ", er)
            print(reply.errorString())"""

