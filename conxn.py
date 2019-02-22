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
        logger.info(r.text)
        return r.text

    def resetConxn(self):
        try:
            controller = Controller.from_port()
            controller.authenticate()
        except stem.SocketError as exc:
            logger.info("Unable to connect to tor on port 9051: {0}".format(exc))
            sys.exit(1)
        try:
            logger.info("Current IP: {0}".format(self.getIp()))
            controller.signal(Signal.NEWNYM)
            logger.info("IP Reset to: {0}".format(self.getIp()))
        except stem.ControllerError as err:
            logger.info("Issue with reset - {0}".format(err))
    
    def getUrlContent(self, url, header=None, inputData=None):
        r = None
        logger.info(header)
        for i in range(0, 50):
            r = requests.get(url, proxies=self.proxyDict, headers=header, data=inputData)
            logger.info(r)
            if r.status_code != 200 and r.status_code != 302:
                time.sleep(5)
                self.resetConxn()
            else:
                self.getIp()
                break
        logger.debug(r.text)
        return r
    
    def postUrlContent(self, url, header=None, inputData=None):
        logger.info(header)
        return requests.post(url, proxies=self.proxyDict, headers=header, data=inputData)
