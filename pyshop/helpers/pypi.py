from xmlrpclib import ServerProxy


proxy = None


def set_proxy(proxy_url):
    global proxy
    proxy = ServerProxy(proxy_url, allow_none=True)


'''
import requests

def list_package(root, package_name):
    return requests.get(u'%s/%s/json' % (root, package_name)).json


def list_package_version(root, package_name, version):
    return requests.get(u'%s/%s/%s/json' %
                        (root, package_name, version)).json
'''