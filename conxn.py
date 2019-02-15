from stem.control import *
from stem import Signal
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Conxn(object):
    def __init__(self):
        self.http_proxy = "http://localhost:8118"
        self.https_proxy = "https://localhost:8118"
        self.proxyDict = {"http": self.http_proxy, "https": self.https_proxy,}

    def getIp(self):
        r = requests.get('https://api.ipify.org?format=json', proxies=self.proxyDict)
        return r.text

    def resetConxn(self):
        try:
            controller = Controller.from_port()
            controller.authenticate()
        except stem.SocketError as exc:
            print("Unable to connect to tor on port 9051: {0}".format(exc))
            sys.exit(1)
        try:
            print("Current IP: {0}".format(self.getIp()))
            controller.signal(Signal.NEWNYM)
            print("IP Reset to: {0}".format(self.getIp()))
        except stem.ControllerError as err:
            print("Issue with reset - {0}".format(err))
    
    def getUrlContent(self, Url):
        r = None
        for i in range(0, 50):
            r = requests.get(Url, proxies=self.proxyDict)
            logger.info(r)
            if r.status_code != 200 and r.status_code != 302:
                time.sleep(5)
                self.resetConxn()
            else:
                break
        print(r.text)
        return r