from base import reactor
from handles.http_server import start_server

import logging
logging.basicConfig(level=logging.DEBUG)

port = 8080
start_server(reactor, port)
reactor.run()