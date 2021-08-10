import requests
import utils.log_utils

log = utils.log_utils.logging_init('file_utils')

def upload_upgrade_image(ip, file_path):

    url = "http://" + ip + ":8080/upload"
    log.debug("%s", ip)
    headers ={
        #'Content-Type': 'application/octet-stream\r\n\r\n'
    }

    files = {
        'file': (open(file_path, 'rb',))
    }

    try:
        r = requests.post(url=url, files=files ).text
        #print(r.status_code)
        #print(r.text)
        #imageUrl = json.loads(r)['result']
        #if imageUrl != None:
        #   imageUrl = imageUrl[0]
    except Exception as e:
        log.error("%s", e)
    #print(r.status_code)
    log.debug("%s", r)