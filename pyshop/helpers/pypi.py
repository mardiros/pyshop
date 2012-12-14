import httplib
from xmlrpclib import ServerProxy, Transport


proxy = None


import xmlrpclib

class ProxiedTransport(Transport):
  # Put here an identification string for your application
  user_agent = 'pyshop'

  def __init__(self, proxy):
    self.proxy = proxy
    self._use_datetime = False

  def make_connection(self, host):
    self.realhost = host
    return httplib.HTTP(self.proxy)

  def send_request(self, connection, handler, request_body):
    connection.putrequest("POST", 'http://%s%s' % (self.realhost, handler))

  def send_host(self, connection, host):
    connection.putheader('Host', self.realhost)



def set_proxy(proxy_url, transport_proxy=None):
    global proxy
    transport = ProxiedTransport(transport_proxy) if transport_proxy else None
    proxy = ServerProxy(proxy_url, transport=transport, allow_none=True)


'''
import requests

def list_package(root, package_name):
    return requests.get(u'%s/%s/json' % (root, package_name)).json


def list_package_version(root, package_name, version):
    return requests.get(u'%s/%s/%s/json' %
                        (root, package_name, version)).json
'''
