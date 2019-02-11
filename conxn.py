from stem.control import *
from stem import Signal
import requests

class Conxn(object):
    def __init__(self):
        self.http_proxy = "http://localhost:8118"
        self.https_proxy = "https://localhost:8118"
        self.proxyDict = {"http": self.http_proxy, "https": self.https_proxy,}

    def printHi(self):
        print('Hi')

    def getIp(self):
        r = requests.get('https://api.ipify.org?format=json', proxies=self.proxyDict)
        print(r.text)
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