from twisted.web import server
from twisted.internet import endpoints
from handler_tree import generate_tree


def start_server(reactor, port=8080):
    site = server.Site(generate_tree())
    ep = endpoints.TCP4ServerEndpoint(reactor, port)
    ep.listen(site)
