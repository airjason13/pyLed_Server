import requests

def upload_client_image(cover_path):
    url = "http://239.11.11.11:8080/upload"
    headers ={
        #'Content-Type': 'application/octet-stream\r\n\r\n'
    }

    files = {
        'file': (open(cover_path, 'rb',))
    }

    try:
        r = requests.post(url=url, files=files ).text
        #print(r.status_code)
        #print(r.text)
        #imageUrl = json.loads(r)['result']
        #if imageUrl != None:
        #   imageUrl = imageUrl[0]
    except Exception as e:
        print(e)
    #print(r.status_code)
    #print(r)