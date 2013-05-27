"""
PyPI XML-RPC Client helper

To use the :data:`pyshop.helpers.pypi.proxy`, the method
:method:`pyshop.helpers.pypi.set_proxy`must be called to
install the XML RPC proxy.

Also it is possible to install an HTTP Proxy in case the pyshop host does not
have a direct access to internet.

This is actually a configuration key ``pyshop.pypi.transport_proxy`` from the
paste ini file.

.. warning::
    This code use an unsecured connection (http)
    and should be modified since PyPI is available in https.

.. :data:`proxy`:: The XML RPC Proxy


"""

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
    """Create the proxy to PyPI XML-RPC Server"""
    global proxy
    transport = ProxiedTransport(transport_proxy) if transport_proxy else None
    proxy = ServerProxy(proxy_url, transport=transport, allow_none=True)
