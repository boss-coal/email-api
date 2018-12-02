from base import reactor
from handles.http_server import start_server

import logging
from handles.setting_handler import initProviders
logging.basicConfig(level=logging.DEBUG)

def initialize():
    initProviders()

def main():
    port = 8080
    start_server(reactor, port)
    reactor.callLater(0, initialize)
    reactor.run()

if __name__ == '__main__':
    main()