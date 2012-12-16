import httplib
from xmlrpclib import ServerProxy, Transport

proxy = None


class ProxiedTransport(Transport):

  user_agent = 'pyshop'

  def __init__(self, proxy):
    self.proxy = proxy
    self._use_datetime = False

  def make_connection(self, host):
    self.realhost = host
    return httplib.HTTP(self.proxy)

  def send_request(self, connection, handler, request_body):
    connection.putrequest('POST', 'http://%s%s' % (self.realhost, handler))

  def send_host(self, connection, host):
    connection.putheader('Host', self.realhost)



def set_proxy(proxy_url, transport_proxy=None):
    global proxy
    transport = ProxiedTransport(transport_proxy) if transport_proxy else None
    proxy = ServerProxy(proxy_url, transport=transport, allow_none=True)
