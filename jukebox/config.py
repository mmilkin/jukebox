def make_root_resource():
    import ConfigParser
    from twisted.internet import reactor

    from jukebox.api import API
    from jukebox.httpd import HTTPd, Stream, Source
    from jukebox.storage import MemoryStorage
    from jukebox.scanner import DirScanner
    from jukebox.song import Song, Playlist
    from jukebox.encoders import CopyEncoder, GSTEncoder

    config = ConfigParser.RawConfigParser()
    config.read('jukebox.cfg')
    folders = config.get('base', 'music_folders')
    storage = MemoryStorage()
    for folder in folders.split(','):
        print folder
        scanner = DirScanner(storage, folder)
        reactor.callInThread(scanner.scan)

    playlist = Playlist()
    api_server = API(storage, playlist)
    source = Source(playlist, GSTEncoder)
    httpd = HTTPd(api_server.app.resource(), Stream(source))
    return httpd.app.resource
resource = make_root_resource()
