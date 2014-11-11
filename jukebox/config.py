import yaml
import zope.interface
from zope.interface.adapter import AdapterRegistry
from zope.interface.interface import adapter_hooks


registry = AdapterRegistry()


def hook(provided, object):
    adapter = registry.lookup1(zope.interface.providedBy(object), provided, '')
    if not adapter:
        return
    return adapter(object)
adapter_hooks.append(hook)


def make_root_resource():
    from jukebox.registry import configure_registry
    configure_registry()

    from twisted.internet import reactor
    from jukebox.api import API
    from jukebox.httpd import HTTPd, Stream, Source
    from jukebox.interfaces import ISearchableStorage

    config = yaml.load(open('jukebox.yaml', 'r'))

    storage = config['storage']

    scanners = config['scanners']
    playlist = config['playlist']
    encoder = config['encoder']

    for scanner in scanners:
        reactor.callInThread(scanner.scan)

    ISearchableStorage(storage).init()  # Defered lost in space

    api_server = API(storage, playlist)
    source = Source(playlist, encoder)
    httpd = HTTPd(api_server.app.resource(), Stream(source))
    return httpd.app.resource


resource = make_root_resource()
