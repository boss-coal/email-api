from twisted.web.resource import Resource
from base_handler import BaseHandler
from test_handler import TestHandler

class Root(BaseHandler):
    isLeaf = False

def generate_tree():
    root = Root()
    # add children
    root.putChild('test', TestHandler())

    return root

