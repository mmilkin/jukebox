import yaml


def make_root_resource():
    from twisted.internet import reactor
    from jukebox.api import API
    from jukebox.httpd import HTTPd, Stream, Source

    config = yaml.load(open('jukebox.yaml', 'r'))


    storage = config['storage']
    scanners = config['scanners']
    playlist = config['playlist']
    encoder = config['encoder']
    for scanner in scanners:
        reactor.callInThread(scanner.scan)
    api_server = API(storage, playlist)
    source = Source(playlist, encoder)
    httpd = HTTPd(api_server.app.resource(), Stream(source))
    return httpd.app.resource

resource = make_root_resource()
